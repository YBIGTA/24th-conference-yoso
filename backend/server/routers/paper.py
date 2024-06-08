from fastapi import APIRouter, Depends
from typing import Annotated
from neo4j import Driver
from pymongo.collection import Collection
from ..database import document, vector, graph


router = APIRouter(
    prefix="/paper",
    tags=["Paper Database"]
)


@router.put(
    path="/create", 
    summary="새 논문 생성"
)
async def upsert_paper(
    body: document.Document,
    driver: Annotated[Driver, Depends(graph.get_graph_db)],
    collection: Annotated[Collection, Depends(document.get_mongo_collection)]
):
    # Insert into document database
    document.upsert_document(collection, body)
    
    # Insert into vector store
    if body.summary is not None:
        vector.create_vector(
            id=body.id,
            domain=body.summary.domain,
            problem=body.summary.problem,
            solution=body.summary.solution
        )
    
    # Insert into graph database
    if body.title is not None and body.reference is not None:
        graph.create_node(driver, body.id, body.title)
        for ref_title in body.reference:
            graph.create_relationship(driver, body.title, ref_title)

    return {
        "created_id": body.id
    }
