from fastapi import APIRouter

from app.api.routes import auth


api_router = APIRouter()

api_router.include_router(
    router=auth.router,
    prefix="/auth",
    tags=["Authentication"]
)
