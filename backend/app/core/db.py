from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from sqlmodel import create_engine

from app.core.config import settings


engine = create_engine(str(settings.SQLALCHEMY_DATABSE_URI))

client = MongoClient(settings.MONGO_URI, server_api=ServerApi("1"))
database = client[settings.MONGO_DATABASE]
collection = database[settings.MONGO_COLLECTION]
