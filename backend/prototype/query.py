import os
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

# Tokenize
model = SentenceTransformer('all-MiniLM-L6-v2')

while True:
    domain = input('도메인 (<q> to quit): ')
    if domain == 'q':
        break
    problem = input('해결하고자 하는 문제: ')
    solution = input('해결 방법: ')

    # TODO: Do something about this
    sentence = f'Domain: {domain}, Problem statement: {problem}, Solution: {solution}'

    query = model.encode(sentence).tolist()

    # Query
    resp_raw = index.query(
        namespace='raw',
        vector=query,
        top_k=1,
    )

    resp_summary = index.query(
        namespace='summary',
        vector=query,
        top_k=1,
    )

    # Result: Raw text
    result_raw = resp_raw['matches'][0]
    doc_id_raw = result_raw['id']
    score_raw = result_raw['score']
    doc_raw = collection.find_one({ '_id': doc_id_raw })

    # Result: Summary
    result_summary = resp_summary['matches'][0]
    doc_id_summary = result_summary['id']
    score_summary = result_summary['score']
    doc_summary = collection.find_one({ '_id': doc_id_summary })

    raw_title = doc_raw['title'] if len(doc_raw['title']) < 55 else doc_raw['title'][:51] + '...'
    summary_title = doc_summary['title'] if len(doc_summary['title']) < 55 else doc_summary['title'][:51] + '...'

    print()
    print(f'┌────────────┬────────┬────────────────────────────────────────────────────────┐')
    print(f'│ Embedding  │ Score  │ Title                                                  │')
    print(f'├────────────┼────────┼────────────────────────────────────────────────────────┤')
    print(f'│ Abstract   │ {score_raw:.4f} │ {raw_title:54} │')
    print(f'├────────────┼────────┼────────────────────────────────────────────────────────┤')
    print(f'│ Summarized │ {score_summary:.4f} │ {summary_title:54} │')
    print(f'└────────────┴────────┴────────────────────────────────────────────────────────┘')
    print('\n'*12)
