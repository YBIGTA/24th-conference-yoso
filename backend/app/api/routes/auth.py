from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.models import Token
from app.core import security
from app.core.config import settings


router = APIRouter()

fake_users_db = {
    "root": {
        "username": "root",
        "full_name": "root",
        "email": "root@bar.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


@router.post(
    path="/login",
    summary="액세스 토큰",
    description="Get OAuth2 compatible access token for future requests.",
    response_model=Token
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = fake_users_db.get(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return Token(
        access_token=security.create_access_token(
            subject=user["username"],
            expires_delta=access_token_expires
        )
    )
    