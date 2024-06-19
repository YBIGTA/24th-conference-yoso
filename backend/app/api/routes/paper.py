from fastapi import APIRouter, HTTPException, status

from app.core.db import collection
from app.crud import get_paper_by_id, upsert_paper
from app.models import Paper


router = APIRouter()


@router.get("/{paper_id}")
def get_paper(
    paper_id: str
):
    paper = get_paper_by_id(collection, paper_id)
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper {paper_id} does not exist"
        )
    return paper
