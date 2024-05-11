import uuid
import os
import json
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENV')
MONGODB_URI = os.getenv('MONGODB_URI')

# Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index('prototype')

# MongoDB client
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
database = client['ybigta-letsur-prototype']
collection = database['documents']

# Generate ID & Embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

with open('dataset-test.json', 'r') as file:
    dataset = json.load(file)

    vectors_raw_text = []
    vectors_summarized = []
    documents = []

    for data in dataset:
        doc_id = str(uuid.uuid4())

        raw_text = f'Title: {data['title']}. Abstract: {data['abstract']}'
        summarized = data['result']['summary']
        keywords = data['result']['keywords']

        embed_raw_text = model.encode(raw_text)
        embed_summarized = model.encode(summarized)

        vectors_raw_text.append({
            'id': doc_id,
            'values': embed_raw_text,
            'metadata': { 'keywords': keywords }
        })

        vectors_summarized.append({
            'id': doc_id,
            'values': embed_summarized,
            'metadata': { 'keywords': keywords }
        })

        documents.append({
            '_id': doc_id,
            'title': data['title'],
            'abstract': data['abstract']
        })

    # Pinecone
    index.upsert(vectors=vectors_raw_text, namespace='raw')
    index.upsert(vectors=vectors_summarized, namespace='summary')

    # MongoDB
    collection.insert_many(documents)
