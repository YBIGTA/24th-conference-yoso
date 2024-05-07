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

    vectors = []
    documents = []

    for data in dataset:
        doc_id = str(uuid.uuid4())

        sentence = f'{data['title']}. {data['abstract']}'
        embedding = model.encode(sentence)

        vectors.append({
            'id': doc_id,
            'values': embedding
        })

        documents.append({
            '_id': doc_id,
            'title': data['title'],
            'abstract': data['abstract']
        })

    # Pinecone
    index.upsert(vectors=vectors, namespace='prototype')

    # MongoDB
    collection.insert_many(documents)
