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
    get_all_upload_staus
)
from app.models import (
    Paper, 
    PaperQuery, 
    PaperSummary,
    PaperInference,
    GraphNodeBase,
    UploadStatus
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
    path="/status",
    summary="Get upload status of all papers",
    response_model=list[UploadStatus]
)
def get_upload_status(
    session: SessionDep
):
    return get_all_upload_staus(session)


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
    # Insert into document database
    upsert_paper(collection, paper_data)
    
    # Insert into vector store
    if paper_data.summary is not None:
        text = PaperQuery(
            domain=paper_data.summary.domain,
            problem=paper_data.summary.problem,
            solution=paper_data.summary.solution
        )
        create_vector(index, paper_data.id, text)
    
    # Insert into graph database
    if paper_data.title is not None:
        node_data = GraphNodeBase(
            paper_id=paper_data.id, title=paper_data.title)
        create_graph_node(driver, node_data)

        if paper_data.reference:
            for ref_title in paper_data.reference:
                create_graph_relationship(driver, paper_data.title, ref_title)

    return get_paper_by_id(collection, paper_data.id)


def detect_bounding_box(file: UploadFile):
    """
    Detect bounding box with LayoutParser
    """
    pass


def parse_metadata(detection) -> PaperInference:
    """
    Parse metadata with LayoutLMv3
    """
    return PaperInference(
        id="default",
        abstract="default abstract text"
    )


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
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": data.abstract}
        ]
    )
    res = completion.choices[0].message.content

    try:
        summary = PaperSummary.model_validate(obj=json.loads(res))
        paper_data = Paper.model_validate(
            obj=(data.model_dump() | {"summary": summary}))
        return paper_data
    except ValidationError as e:
        print(e)
        return None


def handle_upload(
        file: UploadFile, collection: Collection, driver: Driver, index: Index, 
        session: Session, upload_status: UploadStatus):
    """
    Background task for model inference
    """
    # Layout parser
    detection = detect_bounding_box(file)
    upload_status.bbox_detected = True
    upload_status = update_upload_status(session, upload_status)
    
    # LayouLMv3
    parsed_metadata = parse_metadata(detection)
    upload_status.metadata_parsed = True
    upload_status = update_upload_status(session, upload_status)

    # Upload images to S3
    for img_file in []:
        upload_file_to_s3(img_file, "img")
    upload_status.images_uploaded = True
    upload_status = update_upload_status(session, upload_status)

    # Extract summary using OpenAI API
    paper_data = extract_paper_summary(parsed_metadata)
    if not paper_data:
        return
    upload_status.keywords_extracted = True
    upload_status = update_upload_status(session, upload_status)

    # Save to database
    paper = Paper.model_validate(obj=paper_data)
    create_paper(paper, collection, driver, index)
    upload_status.metadata_stored = True
    upload_status = update_upload_status(session, upload_status)

    print(f"INFO:     Background task completed for {file.filename}")


@router.post(
    path="/upload",
    summary="Upload PDF file"
)
async def upload_file(
    file: UploadFile,
    session: SessionDep,
    collection: CollectionDep,
    driver: DriverDep,
    index: IndexDep,
    background_tasks: BackgroundTasks
):
    upload_status = create_upload_status(session, file.filename)
    if not upload_status:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Upload PDF file to S3
    url = upload_file_to_s3(file, "pdf")
    if not url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file"
        )
    upload_status.pdf_uploaded = True
    upload_status = update_upload_status(session, upload_status)

    # Background task
    background_tasks.add_task(
        handle_upload, file, collection, driver, index, session, upload_status)

    return {
        "url": url
    }