from fastapi import APIRouter
from ..database import document

router = APIRouter(
    prefix="/paper",
    tags=["Paper Database"]
)


@router.post("/create", summary="새 논문 생성")
async def create_paper(body: document.Document):
    pass
