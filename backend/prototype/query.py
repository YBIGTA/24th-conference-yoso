import os
import numpy as np
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

NUM_QUERY_RESULTS = 5

# Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)
index_raw = pc.Index('prototype')
index_sum = pc.Index('dps')

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
    sentences = [domain, problem, solution]

    query_raw = model.encode(sentence).tolist()
    query_sum = np.concatenate([emb for emb in model.encode(sentences)]).tolist()

    # Query
    resp_raw = index_raw.query(
        namespace='raw_v2',
        vector=query_raw,
        top_k=NUM_QUERY_RESULTS,
    )

    resp_summary = index_sum.query(
        namespace='summary',
        vector=query_sum,
        top_k=NUM_QUERY_RESULTS,
    )
    # Result: Raw text
    print()
    print(f'┌──────────────────────────────────────────────────────────────────────────────┐')
    print(f'│ {"Abstract": ^76} │')
    print(f'├────────┬─────────────────────────────────────────────────────────────────────┤')
    print(f'│ Score  │ Title                                                               │')
    
    for i in range(NUM_QUERY_RESULTS):
        result_raw = resp_raw['matches'][i]
        doc_id_raw = result_raw['id']
        score_raw = result_raw['score']
        doc_raw = collection.find_one({ '_id': doc_id_raw })

        raw_title = (doc_raw['title'] 
                    if len(doc_raw['title']) < 68 
                    else doc_raw['title'][:64] + '...')
        
        print(f'├────────┼─────────────────────────────────────────────────────────────────────┤')
        print(f'│ {score_raw:.4f} │ {raw_title.replace("\n", ""):67} │')
    
    print(f'└────────┴─────────────────────────────────────────────────────────────────────┘')
        
    # Result: Summary
    print()
    print(f'┌──────────────────────────────────────────────────────────────────────────────┐')
    print(f'│ {"Domain, Problem, Solution": ^76} │')
    print(f'├────────┬─────────────────────────────────────────────────────────────────────┤')
    print(f'│ Score  │ Title                                                               │')
    
    for i in range(NUM_QUERY_RESULTS):
        result_summary = resp_summary['matches'][i]
        doc_id_summary = result_summary['id']
        score_summary = result_summary['score']
        doc_summary = collection.find_one({ '_id': doc_id_summary })
        
        summary_title = (doc_summary['title'] 
                        if len(doc_summary['title']) < 68 
                        else doc_summary['title'][:64] + '...')
        
        print(f'├────────┼─────────────────────────────────────────────────────────────────────┤')
        print(f'│ {score_summary:.4f} │ {summary_title.replace("\n", ""):67} │')

    print(f'└────────┴─────────────────────────────────────────────────────────────────────┘')
        