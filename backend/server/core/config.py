import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Development(BaseSettings):
    load_dotenv()

    # Pinecone
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    PINECONE_ENV: str = os.getenv("PINECONE_ENV")
    PINECONE_INDEX: str = os.getenv("PINECONE_INDEX")

    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE")
    MONGODB_COLLECTION: str = 'documents'

    # Neo4j
    NEO4J_URI: str = 'neo4j://localhost:7687'
    NEO4J_AUTH_USER: str = os.getenv("NEO4J_AUTH_USER")
    NEO4J_AUTH_PASSWORD: str = os.getenv("NEO4J_AUTH_PASSWORD")
    

class Deployment(BaseSettings):
    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_ENV: str
    PINECONE_INDEX: str

    # MongoDB
    MONGODB_URI: str
    MONGODB_DATABASE: str
    MONGODB_COLLECTION: str

    # Neo4j
    NEO4J_URI: str
    NEO4J_AUTH_USER: str
    NEO4J_AUTH_PASSWORD: str


settings = Deployment()
