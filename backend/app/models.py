from sqlmodel import Field, SQLModel
from pydantic import BaseModel


class User(SQLModel, table=True):
    user_id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    hashed_password: str
    first_name: str
    last_name: str
    is_admin: bool = False


class UserRegister(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
