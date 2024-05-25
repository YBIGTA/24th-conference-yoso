from server.core.config import settings
from pymongo.mongo_client import MongoClient
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


class Document(BaseModel):
    id: str
    abstract: str
    body: list[Body]
    impact: int
    keywords: list[str]
    published_year: str | None
    reference: list[str]
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
    **kwargs
) -> str:
    """Creates a document.
    
    Creates a document with given keyword arguments.

    Args:
        **kwargs: Fields for documents. Must satisfy the schema `Document`.

    Returns:
        String ID value of the created document.

    Raises:
        ValidationError
    """
    try:
        kwargs["keywords"] = kwargs.pop("summary")["keywords"]
        doc = Document(**kwargs).model_dump()
        doc["_id"] = doc.pop("id")
        
        result = collection.insert_one(doc)
        
        return result.inserted_id
    except ValidationError as e:
        raise e

