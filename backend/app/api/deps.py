from typing import Annotated, Generator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from neo4j import Driver, GraphDatabase
from pinecone import Index
from pymongo.collection import Collection
from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine, collection, index
from app.core.security import ALGORITHM
from app.models import User, TokenPayload


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_db() -> Generator[Session, None, None]:
    """
    PostgreSQL session.
    """
    with Session(engine) as session:
        yield session


def get_mongo_collection() -> Generator[Collection, None, None]:
    """
    MongoDB collection.
    """
    return collection


def get_pinecone_index() -> Generator[Index, None, None]:
    """
    Pinecone index.
    """
    return index


def get_graph_db() -> Generator[Driver, None, None]:
    """
    Neo4j driver.
    """
    with GraphDatabase.driver(
        uri=settings.NEO4J_URI, 
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
    ) as driver:
        yield driver


SessionDep = Annotated[Session, Depends(get_db)]
CollectionDep = Annotated[Collection, Depends(get_mongo_collection)]
IndexDep = Annotated[Index, Depends(get_pinecone_index)]
DriverDep = Annotated[Driver, Depends(get_graph_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """
    Retrieves the current user based on the provided token.

    Args:
        session: The database session used to query the user.
        token: The JWT token used to identify the user.

    Returns:
        The User object corresponding to the token's subject if found.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_admin_user(current_user: CurrentUser) -> User:
    """
    Retrieves the current admin user if the user has admin privileges.

    Args:
        current_user: The current user object obtained through dependency 
          injection. The user must have admin privileges.

    Returns:
        The current user object if the user has admin privileges.

    Raises:
        HTTPException: If the user does not have admin privileges.
    """
    if not current_user.is_admin:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
