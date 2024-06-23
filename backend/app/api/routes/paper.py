from fastapi import APIRouter, HTTPException, status

from app.api.deps import CollectionDep, DriverDep, IndexDep
from app.core.db import collection
from app.crud import (
    get_paper_by_id, 
    get_vector_ids_by_sentence, 
    get_vectors_by_ids, 
    get_citation_nodes, 
    get_reference_nodes, 
    upsert_paper, 
    create_vector,
    create_graph_node,
    create_graph_relationship
)
from app.models import (
    Paper, 
    PaperQuery, 
    PaperCore, 
    PaperGraph, 
    PaperScore, 
    GraphNodeBase
)
from app.utils import create_embedding, filter_by_similarity


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


@router.post(
    path="/search", 
    summary="Search top 5 papers based on query text", 
    response_model=list[PaperCore]
)
async def retrieve_core_papers(
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
    path="/search/graph", 
    summary="Search subgraph nodes given root node", 
    response_model=list[PaperScore]
)
async def construct_graph(
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
