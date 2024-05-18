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
index_384 = pc.Index('384')
index_768 = pc.Index('768')

# MongoDB client
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
database = client['ybigta-letsur-prototype']
collection = database['documents']

# Generate ID & Embeddings
models = [
    'all-MiniLM-L6-v2',
    'multi-qa-MiniLM-L6-cos-v1',
    'paraphrase-albert-small-v2',
    'all-distilroberta-v1',
    'multi-qa-distilbert-cos-v1'
]
model_1 = SentenceTransformer(models[0])
model_2 = SentenceTransformer(models[1])
model_3 = SentenceTransformer(models[2])
model_4 = SentenceTransformer(models[3])
model_5 = SentenceTransformer(models[4])


def concat_embedding(
    model: SentenceTransformer,
    domain: str, 
    problem: str, 
    solution: str
) -> np.ndarray:
    embeddings = model.encode([domain, problem, solution])
    return np.concatenate([emb for emb in embeddings])


with open('dataset-test-DPS.json', 'r') as file:
    dataset = json.load(file)

    vectors_1 = []
    vectors_2 = []
    vectors_3 = []
    vectors_4 = []
    vectors_5 = []
    # documents = []

    for idx, data in enumerate(dataset):
        doc_id = str(uuid.uuid4())

        try:
            # raw_text = f'Title: {data['title']}. Abstract: {data['abstract']}'
            title = data['title']
            domain = data['result']['domain']
            problem = data['result']['problem']
            solution = data['result']['solution']
            keywords = data['result']['keywords']

            # Make embeddings
            emb_1 = concat_embedding(model_1, domain, problem, solution)
            emb_2 = concat_embedding(model_2, domain, problem, solution)
            emb_3 = concat_embedding(model_3, domain, problem, solution)
            emb_4 = concat_embedding(model_4, domain, problem, solution)
            emb_5 = concat_embedding(model_5, domain, problem, solution)
            
            # embed_raw_text = model.encode(raw_text)
            # embed_summarized = concat_embedding(domain, problem, solution)

            # Raw embedding
            vectors_1.append({
                'id': doc_id,
                'values': emb_1,
                'metadata': { 'title': title }
            })

            vectors_2.append({
                'id': doc_id,
                'values': emb_2,
                'metadata': { 'title': title }
            })

            vectors_3.append({
                'id': doc_id,
                'values': emb_3,
                'metadata': { 'title': title }
            })

            vectors_4.append({
                'id': doc_id,
                'values': emb_4,
                'metadata': { 'title': title }
            })

            vectors_5.append({
                'id': doc_id,
                'values': emb_5,
                'metadata': { 'title': title }
            })

            # vectors_raw_text.append({
            #     'id': doc_id,
            #     'values': embed_raw_text,
            #     'metadata': { 'keywords': keywords }
            # })

            # Summary embedding
            # vectors_summarized.append({
            #     'id': doc_id,
            #     'values': embed_summarized,
            #     'metadata': { 'keywords': keywords }
            # })

            # Parsed document
            # documents.append({
            #     '_id': doc_id,
            #     'title': data['title'],
            #     'abstract': data['abstract']
            # })
        except Exception as e:
            print(f"Error inserting data {idx}:")
            print(e)

    # Pinecone
    # index_raw.upsert(vectors=vectors_raw_text, namespace='raw_v2')
    # index_sum.upsert(vectors=vectors_summarized, namespace='summary')
    index_384.upsert(vectors=vectors_1, namespace=models[0])
    index_384.upsert(vectors=vectors_2, namespace=models[1])
    index_768.upsert(vectors=vectors_3, namespace=models[2])
    index_768.upsert(vectors=vectors_4, namespace=models[3])
    index_768.upsert(vectors=vectors_5, namespace=models[4])

    # MongoDB
    # collection.insert_many(documents)
