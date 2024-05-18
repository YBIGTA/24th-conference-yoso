import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Development(BaseSettings):
    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_ENV: str

    # MongoDB
    MONGODB_URI: str
    MONGODB_DATABASE: str
    
    model_config = SettingsConfigDict(env_file='../.env')
    

class Deployment(BaseSettings):
    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_ENV: str

    # MongoDB
    MONGODB_URI: str
    MONGODB_DATABASE: str


settings = Development()
