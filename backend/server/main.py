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
        "title": doc["title"],
    } for doc in docs]

    return {
        "results": results
    }
