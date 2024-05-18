from server.config.core import settings
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

MONGODB_URI = settings.MONGODB_URI
MONGODB_DATABASE = settings.MONGODB_DATABASE
MONGODB_COLLECTION = settings.MONGODB_COLLECTION

# MongoDB client
client = MongoClient(MONGODB_URI, server_api=ServerApi("1"))
database = client[MONGODB_DATABASE]
collection = database[MONGODB_COLLECTION]


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


