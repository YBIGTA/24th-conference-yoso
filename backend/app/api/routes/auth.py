from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep, CurrentUser
from app.core.security import create_access_token
from app.core.config import settings
from app.crud import create_user, get_user_by_email, authenticate_user
from app.models import User, UserRegister, Token


router = APIRouter()


@router.post(
    path="/login",
    summary="Get access token",
    description="Get OAuth2 compatible access token for future requests.",
    response_model=Token
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
):
    user = authenticate_user(
        session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return Token(
        access_token=create_access_token(
            subject=user.user_id,
            expires_delta=access_token_expires
        )
    )


@router.post(
    path="/register",
    summary="Register user",
    description="Register a user with given email and password.",
)
def register(
    user_data: UserRegister,
    session: SessionDep,
):
    user = get_user_by_email(session, user_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {user_data.email} already exists.",
        )
    user = create_user(session, user_data)

    return user


@router.get(
    path="/me",
    summary="Get current user",
    description="Get current user",
)
def get_user_me(
    current_user: CurrentUser
) -> User | None:
    return current_user
