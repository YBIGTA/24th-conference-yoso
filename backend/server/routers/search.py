from fastapi import APIRouter, Body, Depends
from neo4j import Driver
from pydantic import BaseModel
from typing import Annotated
from ..database import vector, document, graph


class SearchBody(BaseModel):
    domain: str
    problem: str
    solution: str


router = APIRouter(
    prefix="/search",
    tags=["Search Papers"]
)


@router.post("/core", summary="핵심 페이퍼 도출")
async def retrieve_core_papers(body: SearchBody):
    # Retrieve top 5 relevant paper ids
    doc_ids = vector.search_by_sentence(
        domain=body.domain, 
        problem=body.problem,
        solution=body.solution, 
        k=5
    )

    # Fetch title, year, keywords from document database
    docs = [document.search_by_id(id) for id in doc_ids]
    
    results = [{
        "id": doc["_id"],
        "title": doc["title"].replace("-\n", "").replace("\n", " "),
        "published_year": doc["published_year"],
        "keywords": doc["keywords"]
    } for doc in docs]

    return results


@router.post("/graph", summary="루트 노드 기반 그래프 구성")
async def construct_graph(
    num_nodes: Annotated[int, Body()],
    root_id: Annotated[str, Body()], 
    query: SearchBody,
    driver: Annotated[Driver, Depends(graph.get_graph_db)]
):
    # Fetch ids of adjacent nodes
    references = graph.match_referencing_nodes(driver, root_id)
    citations = graph.match_referenced_nodes(driver, root_id)

    # Fetch embeddings of adjacent nodes
    ref_vecs = vector.fetch_all_by_id(references) if references else []
    cit_vecs = vector.fetch_all_by_id(citations) if citations else []

    # Rank by similarity score from dps query
    query_vector = vector.create_embedding(**query.model_dump())
    ref_scores = vector.rank_by_similarity(
        src=query_vector,
        tgt=ref_vecs + cit_vecs,
        k=num_nodes
    )
    scores_of = {elem["id"]: elem["score"] for elem in ref_scores}

    docs = [document.search_by_id(id) for id in scores_of.keys()]

    return [{
        "id": doc["_id"],
        "title": doc["title"].replace("-\n", "").replace("\n", " "),
        "impact": doc["impact"],
        "score": scores_of[doc["_id"]]
    } for doc in docs]
