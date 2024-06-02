from server.core.config import settings
from pymongo.mongo_client import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.server_api import ServerApi
from pymongo.results import InsertOneResult
from pydantic import BaseModel, ValidationError

MONGODB_URI = settings.MONGODB_URI
MONGODB_DATABASE = settings.MONGODB_DATABASE
MONGODB_COLLECTION = settings.MONGODB_COLLECTION

# MongoDB client
client = MongoClient(MONGODB_URI, server_api=ServerApi("1"))
database = client[MONGODB_DATABASE]
collection = database[MONGODB_COLLECTION]


class Body(BaseModel):
    paragraph_id: int
    section: str
    text: str


class Figure(BaseModel):
    idx: int
    name: str
    caption: str
    related: list[int]
    summary: str


class Summary(BaseModel):
    domain: str
    problem: str
    solution: str
    keywords: list[str]


class Document(BaseModel):
    id: str
    abstract: str
    body: list[Body]
    impact: int = 0
    summary: Summary
    published_year: str | None = None
    reference: list[str]
    figures: list[Figure] = []
    tables: list[Figure] = []
    title: str


def search_by_id(
    id: str
) -> dict:
    """Fetches a document by ID.
    
    Fetch a single document with given ID from database.

    Args:
        id: ID of the document to fetch.
    
    Returns:
        A dict representing corresponding document.
    """
    docs = collection.find_one({ "_id": id })

    return docs


def create_document(
    document: Document
) -> str:
    """Upserts a document.
    
    Updates a document using data from `document`. If no document exists with 
    given id, create one.

    Args:
        document: Fields for documents. Must satisfy the schema `Document`.

    Returns:
        String ID value of the upserted document.

    Raises:
        ValidationError: Arguments do not match the schema.
    """
    try:
        document = document.model_dump()
        document["_id"] = document.pop("id")
        
        # result = collection.insert_one(document)
        result = collection.update_one(
            filter={ "_id": document["_id"] },
            update={ "$set": document },
            upsert=True
        )
        
        return result.upserted_id
    except ValidationError as e:
        raise e
