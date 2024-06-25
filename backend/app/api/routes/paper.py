import json

from fastapi import (
    APIRouter, 
    BackgroundTasks, 
    HTTPException, 
    UploadFile, 
    status
)
from openai import OpenAI

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
    PaperSummary,
    GraphNodeBase,
    UploadStatus
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


def handle_upload(
        file: UploadFile, collection: CollectionDep, driver: DriverDep, 
        index: IndexDep, session: SessionDep, upload_status: UploadStatus):
    ##### Start inference
    pass
    parsed_data = {"id": "hello-world", "abstract": "Most recent semantic segmentation methods adopt\na fully-convolutional network (FCN) with an encoder-\ndecoder architecture. The encoder progressively reduces\nthe spatial resolution and learns more abstract/semantic\nvisual concepts with larger receptive fields. Since context\nmodeling is critical for segmentation, the latest efforts have\nbeen focused on increasing the receptive field, through ei-\nther dilated/atrous convolutions or inserting attention mod-\nules. However, the encoder-decoder based FCN architec-\nture remains unchanged. In this paper, we aim to provide\nan alternative perspective by treating semantic segmenta-\ntion as a sequence-to-sequence prediction task. Specifically,\nwe deploy a pure transformer (i.e., without convolution and\nresolution reduction) to encode an image as a sequence of\npatches. With the global context modeled in every layer of\nthe transformer, this encoder can be combined with a simple\ndecoder to provide a powerful segmentation model, termed\nSEgmentation TRansformer (SETR). Extensive experiments\nshow that SETR achieves new state of the art on ADE20K\n(50.28% mIoU), Pascal Context (55.83% mIoU) and com-\npetitive results on Cityscapes. Particularly, we achieve the\nfirst position in the highly competitive ADE20K test server\nleaderboard on the day of submission."}
    ##### End inference
    upload_status.bbox_detected = True
    upload_status.metadata_parsed = True
    upload_status = update_upload_status(session, upload_status)

    # Upload images to S3
    pass
    upload_status.images_uploaded = True
    upload_status = update_upload_status(session, upload_status)

    # Extract summary using OpenAI API
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are an assistant for writing academic papers. You are skilled at extracting research domain, problems of previous studies, solution to the problem in single sentence and keywords. Your answer must be in format of JSON {\"domain\": string, \"problem\": string, \"solution\": string, \"keywords\": [string]}."},
            {"role": "user", "content": parsed_data["abstract"]}
        ]
    )
    raw_resp = completion.choices[0].message.content
    try:
        summary = PaperSummary.model_validate(
            obj=json.loads(raw_resp.replace("'", '"'))
        )
        parsed_data["summary"] = summary
        upload_status.keywords_extracted = True
        upload_status = update_upload_status(session, upload_status)
    except Exception as e:
        print(e)

    # Save to database
    paper = Paper.model_validate(obj=parsed_data)
    create_paper(paper, collection, driver, index)
    upload_status.metadata_stored = True
    upload_status = update_upload_status(session, upload_status)


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