from fastapi import APIRouter, Body, Depends
from neo4j import Driver
from pymongo.collection import Collection
from pydantic import BaseModel
from typing import Annotated
from ..database import vector, document, graph


class SearchCoreBody(BaseModel):
    domain: str
    problem: str
    solution: str


class SearchCoreResponse(BaseModel):
    id: str
    title: str
    published_year: str
    keywords: list[str]
    citations: int


class SearchGraphResponse(BaseModel):
    id: str
    title: str
    published_year: str
    keywords: list[str]
    citations: int
    score: float


class SearchSummaryResponse(BaseModel):
    idx: int
    name: str
    caption: str
    summary: str


router = APIRouter(
    prefix="/search",
    tags=["Search Papers"]
)


@router.post(
    path="/core", 
    summary="핵심 페이퍼 도출", 
    response_model=list[SearchCoreResponse]
)
async def retrieve_core_papers(
    body: SearchCoreBody,
    collection: Annotated[Collection, Depends(document.get_mongo_collection)]
):
    # Retrieve top 5 relevant paper ids
    doc_ids = vector.search_by_sentence(
        domain=body.domain, 
        problem=body.problem,
        solution=body.solution, 
        k=5
    )

    # Fetch title, year, keywords from document database
    docs = [document.fetch_by_id(collection, id) for id in doc_ids]
    
    results = [{
        "id": doc.id,
        "title": doc.title.replace("-\n", "").replace("\n", " "),
        "published_year": doc.published_year,
        "keywords": doc.summary.keywords,
        "citations": doc.impact
    } for doc in docs]

    return results


@router.post(
    path="/graph", 
    summary="루트 노드 기반 그래프 구성", 
    response_model=list[SearchGraphResponse]
)
async def construct_graph(
    num_nodes: Annotated[int, Body()],
    root_id: Annotated[str, Body()], 
    query: SearchCoreBody,
    driver: Annotated[Driver, Depends(graph.get_graph_db)],
    collection: Annotated[Collection, Depends(document.get_mongo_collection)]
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

    docs = [document.fetch_by_id(collection, id) for id in scores_of.keys()]

    return [{
        "id": doc.id,
        "published_year": doc.published_year,
        "title": doc.title.replace("-\n", "").replace("\n", " "),
        "citations": doc.impact,
        "score": scores_of[doc.id],
        "keywords": doc.summary.keywords
    } for doc in docs]


@router.get(
    path="/summary/{paper_id}",
    summary="특정 논문의 요약 정보 반환",
    response_model=list[SearchSummaryResponse]
)
async def fetch_summary(
    paper_id: str,
    collection: Annotated[Collection, Depends(document.get_mongo_collection)]
):
    # Fetch document from id
    doc = document.fetch_by_id(collection, paper_id)

    return [{
        "idx": fig.idx,
        "name": fig.name,
        "caption": fig.caption,
        "summary": fig.summary
    } for fig in doc.figures + doc.tables]

