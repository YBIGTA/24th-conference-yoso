from fastapi import APIRouter

from app.api.routes import auth, paper, search


api_router = APIRouter()

api_router.include_router(
    router=auth.router,
    prefix="/auth",
    tags=["Authentication"]
)
api_router.include_router(
    router=paper.router,
    prefix="/paper",
    tags=["Manage Papers"]
)
api_router.include_router(
    router=search.router,
    prefix="/search",
    tags=["Search Papers"]
)