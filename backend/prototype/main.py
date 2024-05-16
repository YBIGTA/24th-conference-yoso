import uuid
import os
import json
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import numpy as np

# Environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENV')
MONGODB_URI = os.getenv('MONGODB_URI')

# Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)
index_raw = pc.Index('prototype')
index_sum = pc.Index('dps')

# MongoDB client
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
database = client['ybigta-letsur-prototype']
collection = database['documents']

# Generate ID & Embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')


def concat_embedding(domain: str, problem: str, solution: str) -> np.ndarray:
    embeddings = model.encode([domain, problem, solution])
    return np.concatenate([emb for emb in embeddings])


with open('dataset-test-DPS.json', 'r') as file:
    dataset = json.load(file)

    vectors_raw_text = []
    vectors_summarized = []
    documents = []

    for data in dataset:
        doc_id = str(uuid.uuid4())

        try:
            raw_text = f'Title: {data['title']}. Abstract: {data['abstract']}'
            domain = data['result']['domain']
            problem = data['result']['problem']
            solution = data['result']['solution']
            keywords = data['result']['keywords']

            # Make embeddings
            embed_raw_text = model.encode(raw_text)
            embed_summarized = concat_embedding(domain, problem, solution)

            # Raw embedding
            vectors_raw_text.append({
                'id': doc_id,
                'values': embed_raw_text,
                'metadata': { 'keywords': keywords }
            })

            # Summary embedding
            vectors_summarized.append({
                'id': doc_id,
                'values': embed_summarized,
                'metadata': { 'keywords': keywords }
            })

            # Parsed document
            documents.append({
                '_id': doc_id,
                'title': data['title'],
                'abstract': data['abstract']
            })
        except Exception as e:
            print(f"Error inserting data:")
            print(e)

    # Pinecone
    index_raw.upsert(vectors=vectors_raw_text, namespace='raw_v2')
    index_sum.upsert(vectors=vectors_summarized, namespace='summary')

    # MongoDB
    collection.insert_many(documents)
