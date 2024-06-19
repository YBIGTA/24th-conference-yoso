from sqlmodel import Field, SQLModel
from pydantic import BaseModel


class PaperBody(BaseModel):
    paragraph_id: int
    section: str
    text: str


class PaperFigure(BaseModel):
    idx: int
    name: str
    caption: str
    related: list[int]
    summary: str


class PaperSummary(BaseModel):
    domain: str
    problem: str
    solution: str
    keywords: list[str]


class Paper(BaseModel):
    id: str
    abstract: str = None
    body: list[PaperBody] = None
    impact: int = None
    summary: PaperSummary = None
    published_year: str = None
    reference: list[str] = None
    figures: list[PaperFigure] = None
    tables: list[PaperFigure] = None
    title: str = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: int | None = None
    exp: int | None = None


class UserBase(SQLModel):
    username: str = Field(unique=True)
    full_name: str | None = None


class User(UserBase, table=True):
    user_id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    is_admin: bool = False


class UserRegister(UserBase):
    password: str
