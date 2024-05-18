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
    MONGODB_COLLECTION: str = os.getenv("MONGODB_COLLECTION")
    

class Deployment(BaseSettings):
    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_ENV: str
    PINECONE_INDEX: str

    # MongoDB
    MONGODB_URI: str
    MONGODB_DATABASE: str
    MONGODB_COLLECTION: str


settings = Development()
