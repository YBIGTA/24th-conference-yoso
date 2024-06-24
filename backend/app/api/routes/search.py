from fastapi import APIRouter

from app.api.deps import CollectionDep, DriverDep, IndexDep
from app.crud import (
    get_vector_ids_by_sentence,
    get_paper_by_id,
    get_reference_nodes,
    get_citation_nodes,
    get_vectors_by_ids
)
from app.models import (
    PaperCore,
    PaperQuery,
    PaperScore,
    PaperGraph,

)
from app.utils import create_embedding, filter_by_similarity


router = APIRouter()


@router.post(
    path="/query", 
    summary="Search top 5 papers based on query text", 
    response_model=list[PaperCore]
)
async def search_papers_by_query(
    body: PaperQuery,
    collection: CollectionDep,
    index: IndexDep
):
    # Retrieve top 5 relevant paper ids
    paper_ids = get_vector_ids_by_sentence(
        index=index,
        text=body,
        k=5
    )

    # Fetch title, year, keywords from document database
    papers = [get_paper_by_id(collection, id) for id in paper_ids]

    return [PaperCore(**paper.model_dump()) for paper in papers 
            if paper is not None]


@router.post(
    path="/graph", 
    summary="Search subgraph nodes given root node", 
    response_model=list[PaperScore]
)
async def search_subgraph(
    body: PaperGraph, 
    collection: CollectionDep,
    driver: DriverDep,
    index: IndexDep
):
    # Fetch ids of adjacent nodes
    references = get_reference_nodes(driver, body.root_id)
    citations = get_citation_nodes(driver, body.root_id)

    # Fetch embeddings of adjacent nodes
    vectors = (get_vectors_by_ids(index, references) 
               + get_vectors_by_ids(index, citations))
    print(vectors)

    # Rank by similarity score
    query_vector = create_embedding(**body.query.model_dump())
    similarity_scores = filter_by_similarity(
        src=query_vector,
        tgt_list=vectors,
        k=body.num_nodes
    )
    scores_dict = {elem["id"]: elem["score"] for elem in similarity_scores}

    # Get filtered document info 
    papers = [get_paper_by_id(collection, id).model_dump() 
              | {"score": scores_dict[id]} for id in scores_dict.keys()]

    return [PaperScore(**paper) for paper in papers]
