from typing import Annotated

from pydantic import AnyUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"

    BACKEND_CORS_ORIGINS: list[AnyUrl] | str = []
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


settings = Settings()
