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
print('=' * 80)
sentence = input('Prompt (<q> to quit): ')
print('=' * 80)

while sentence != 'q':
    x_query = model.encode(sentence).tolist()

    # Query
    resp = index.query(
        namespace='prototype',
        vector = x_query,
        top_k=1,
    )

    result = resp['matches'][0]
    doc_id = result['id']
    score = result['score']

    # MongoDB
    doc = collection.find_one({
        '_id': doc_id,
    })

    print('<QUERY>')
    print(sentence)
    print('\n<SCORE>')
    print(score)
    print('\n<ID>')
    print(doc_id)
    print('\n<TITLE>')
    print(doc['title'])
    print('\n<ABSTRACT>')
    print(doc['abstract'])
    print('=' * 80)

    sentence = input('Prompt (<q> to quit): ')
    print('=' * 80)
