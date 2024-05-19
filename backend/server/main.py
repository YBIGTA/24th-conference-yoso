import numpy as np
from fastapi import FastAPI
from server.database import vector, document

app = FastAPI()


@app.get("/ping")
def read_root():
    return "pong"


@app.get("/search")
async def search(domain: str, problem: str, solution: str):
    doc_ids = vector.search_by_sentence(domain, problem, solution, 5)
    docs = [document.search_by_id(id) for id in doc_ids]
    
    results = [{
        "id": doc["_id"],
        "title": doc["title"].replace("-\n", "").replace("\n", " "),
    } for doc in docs]

    return {
        "results": results
    }


@app.get("/similarity")
async def similarity(domain: str, problem: str, solution: str, k: int):
    ids = [
        "59b63f10-57e0-4f1d-a013-32c141e196cd",
        "d31b2761-7b9f-44c5-9df3-51d5c612296d",
        "d18dfbc2-9125-461a-9951-fa844a19e91c",
        "464956be-8b26-4fc2-a974-e33b37e23d19",
    ]

    query = vector.create_embedding(domain, problem, solution)
    targets = vector.fetch_all_by_id(ids)

    result = vector.rank_by_similarity(query, targets, k)

    return {
        "result": result
    }
