
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app.models import *


engine = create_engine(str(settings.SQLALCHEMY_DATABSE_URI))
