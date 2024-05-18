import numpy as np
from fastapi import FastAPI
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from server.config.core import settings
from server.database import vector

MONGODB_URI = settings.MONGODB_URI

app = FastAPI()

# MongoDB client
client = MongoClient(MONGODB_URI, server_api=ServerApi("1"))
database = client["ybigta-letsur-prototype"]
collection = database["documents"]


@app.get("/ping")
def read_root():
    return "pong"


@app.get("/search")
async def search(domain: str, problem: str, solution: str):
    doc_ids = vector.search_by_sentence(domain, problem, solution, 5)
    docs = [collection.find_one({ "_id": id }) for id in doc_ids]
    results = [{
        "id": doc["_id"],
        "title": doc["title"],
    } for doc in docs]

    return {
        "results": results
    }
