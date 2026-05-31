from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.features.reviews import service
from app.features.reviews.schemas import CreateReviewRequest, ReviewResponse
from app.shared.exceptions import AppException

router = APIRouter()


@router.post("/", response_model=ReviewResponse, status_code=201)
async def submit_review(
    request: CreateReviewRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    writer_email = current_user.get("sub")
    if not writer_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return await service.submit_review(db, writer_email, request)
