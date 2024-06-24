from fastapi import APIRouter, HTTPException, status, UploadFile

from app.api.deps import CollectionDep, DriverDep, IndexDep, SessionDep
from app.core.db import collection
from app.crud import (
    get_paper_by_id, 
    upsert_paper, 
    create_vector,
    create_graph_node,
    create_graph_relationship,
    create_upload_status,
    update_upload_status
)
from app.models import (
    Paper, 
    PaperQuery, 
    GraphNodeBase
)
from app.utils import upload_file_to_s3


router = APIRouter()


@router.get("/{paper_id}")
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


@router.post(
    path="/upload",
    summary="Upload PDF file"
)
async def upload_file(
    file: UploadFile,
    session: SessionDep
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

    return {
        "url": url
    }