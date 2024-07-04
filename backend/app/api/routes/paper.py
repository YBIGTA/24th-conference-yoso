import json

from fastapi import (
    APIRouter, 
    BackgroundTasks, 
    HTTPException, 
    UploadFile, 
    status
)
from neo4j import Driver
from openai import OpenAI
from pinecone import Index
from pydantic_core import ValidationError
from pymongo.collection import Collection
from sqlmodel import Session

from app.api.deps import CollectionDep, DriverDep, IndexDep, SessionDep
from app.core.db import collection
from app.crud import (
    get_paper_by_id, 
    upsert_paper, 
    create_vector,
    create_graph_node,
    create_graph_relationship,
    create_upload_status,
    update_upload_status,
    get_all_upload_staus,
    get_upload_status_by_request_id
)
from app.models import (
    Paper, 
    PaperQuery, 
    PaperSummary,
    PaperInference,
    GraphNodeBase,
    UploadStatus,
    UploadStatusCreate,
    UpdateUploadStatus
)
from app.utils import upload_file_to_s3


router = APIRouter()


@router.get("/item/{paper_id}")
def get_paper(
    paper_id: str
):
    paper = get_paper_by_id(collection, paper_id)
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper {paper_id} does not exist"
        )
    return paper


@router.get(
    path="/status/all",
    summary="Get upload status of all papers",
    response_model=list[UploadStatus]
)
def get_upload_status(
    session: SessionDep
):
    return get_all_upload_staus(session)


@router.post(
    path="/status",
    summary="Create upload status of given paper",
    response_model=UploadStatus
)
def post_upload_status(
    session: SessionDep,
    filename: UploadStatusCreate
):
    return create_upload_status(session, filename.filename)


@router.put(
    path="/status",
    summary="Update upload status of given paper"
)
def put_upload_status(
    session: SessionDep,
    status_data: UpdateUploadStatus
):
    current_status = get_upload_status_by_request_id(
        session, status_data.request_id)
    status_data = status_data.model_dump()
    new_status_data = current_status.model_dump() | {
        key: status_data[key] for key in status_data 
        if status_data[key] is not None
    }
    new_status = UploadStatus.model_validate(obj=new_status_data)
    return update_upload_status(session, new_status)


def extract_paper_summary(data: PaperInference) -> Paper:
    """
    Extract domain, problem, solution and keywords using OpenAI API
    """
    client = OpenAI()

    prompt = """You are an assistant for writing academic papers. You are 
    skilled at extracting research domain, problems of previous studies, 
    solution to the problem in single sentence and keywords. Your answer must 
    be in format of JSON {\"domain\": string, \"problem\": string, \"solution\"
    : string, \"keywords\": [string]}."""
    
    if data.abstract is None:
        return data
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": data.abstract}
        ]
    )
    res = completion.choices[0].message.content
    print(f"DEBUG:    OpenAI response {res}")

    try:
        summary = PaperSummary.model_validate(obj=json.loads(res))
        paper_data = Paper.model_validate(
            obj=(data.model_dump() | {"summary": summary}))
        return paper_data
    except ValidationError as e:
        print(e)
        return data
    

@router.put(
    path="/create",
    summary="Create or update a paper",
    response_model=Paper,
)
def create_paper(
    paper_data: Paper,
    collection: CollectionDep,
    driver: DriverDep,
    index: IndexDep
):
    # Insert into vector store
    if paper_data.summary is None:
        paper_data = extract_paper_summary(
            PaperInference.model_validate(obj=paper_data))
    print(paper_data)
    text = PaperQuery(
        domain=paper_data.summary.domain,
        problem=paper_data.summary.problem,
        solution=paper_data.summary.solution
    )
    create_vector(index, paper_data.id, text)

    # Insert into document database
    upsert_paper(collection, paper_data)
    
    # Insert into graph database
    if paper_data.title is not None:
        node_data = GraphNodeBase(
            paper_id=paper_data.id, title=paper_data.title)
        create_graph_node(driver, node_data)

        if paper_data.reference:
            for ref_title in paper_data.reference:
                create_graph_relationship(driver, paper_data.title, ref_title)

    return get_paper_by_id(collection, paper_data.id)
