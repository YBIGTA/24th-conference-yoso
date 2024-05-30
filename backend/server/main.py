import numpy as np
import json
from fastapi import FastAPI
from server.database import vector, document, graph
from pydantic import BaseModel
from .routers import search

app = FastAPI()
app.include_router(
    router=search.router,
    prefix="/api/v1"
)


@app.get("/ping")
def read_root():
    return "pong"


class SearchBody(BaseModel):
    domain: str
    problem: str
    solution: str


@app.post("/search", summary="핵심 페이퍼 도출")
async def search(body: SearchBody):
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


@app.get("/reset")
def hard_reset_database():
    try:
        with open("server/merged.json", "r") as file:
            data = json.load(file)
            for elem in data:
                # MongoDB
                document.create_document(**elem)

                # Vector
                # vector.create_vector(
                #     id=elem["id"],
                #     domain=elem["summary"]["domain"],
                #     problem=elem["summary"]["problem"],
                #     solution=elem["summary"]["solution"]
                # )

                # Graph
                # graph.create_node(
                #     # driver=driver, 
                #     id=elem["id"],
                #     title=elem["title"]
                # )

                # for ref_title in elem["reference"]:
                #     graph.create_relationship(
                #         # driver=driver,
                #         title=elem["title"],
                #         ref_title=ref_title
                #     )
        return "Success"
    except Exception as e:
        return f"Failed: {e}"