import os
import numpy as np
from fastapi import FastAPI
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from .config import settings

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
MONGODB_URI = os.getenv("MONGODB_URI")

app = FastAPI()

pc = Pinecone(api_key=PINECONE_API_KEY)
index_raw = pc.Index("prototype")
index_sum = pc.Index("dps")

model = SentenceTransformer("all-MiniLM-L6-v2")

# MongoDB client
client = MongoClient(MONGODB_URI, server_api=ServerApi("1"))
database = client["ybigta-letsur-prototype"]
collection = database["documents"]


@app.get("/")
def read_root():
    return {
        "pinecone-env": settings.PINECONE_ENV
    }


@app.get("/search")
async def search(domain: str, problem: str, solution: str):

    sentences = [domain, problem, solution]
    query_sum = np.concatenate([emb for emb in model.encode(sentences)]).tolist()

    resp_summary = index_sum.query(
        namespace="summary",
        vector=query_sum,
        top_k=5,
    )

    doc_ids = [vec["id"] for vec in resp_summary["matches"]]
    docs = [collection.find_one({ "_id": id }) for id in doc_ids]
    results = [{
        "id": doc["_id"],
        "title": doc["title"],
    } for doc in docs]

    return {
        "results": results
    }
