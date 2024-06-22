from typing import Annotated

from pydantic import (
    AnyUrl,
    PostgresDsn,
    computed_field,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"

    BACKEND_CORS_ORIGINS: list[AnyUrl] | str = []
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    MONGO_URI: str
    MONGO_DATABASE: str
    MONGO_COLLECTION: str

    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str

    PINECONE_API_KEY: str
    PINECONE_INDEX: str
    

    @computed_field
    @property
    def SQLALCHEMY_DATABSE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql",
            username=self.POSTGRES_USERNAME,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()
