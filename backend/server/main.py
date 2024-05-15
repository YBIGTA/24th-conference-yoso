from fastapi import FastAPI
from .config import settings


app = FastAPI()


@app.get("/")
def read_root():
    return {
        "pinecone-env": settings.PINECONE_ENV
    }
