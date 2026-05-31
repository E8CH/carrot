from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.reviews.models import Review
from app.shared.exceptions import AppException


async def get_review_by_post_writer(
    db: AsyncSession, post_id: int, writer_email: str
) -> Review | None:
    stmt = select(Review).where(
        Review.post_id == post_id,
        Review.writer_email == writer_email,
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def create_review(
    db: AsyncSession,
    *,
    post_id: int,
    writer_email: str,
    target_email: str,
    is_positive: bool,
    tags: list[str],
    comment: str | None,
) -> Review:
    review = Review(
        post_id=post_id,
        writer_email=writer_email,
        target_email=target_email,
        is_positive=is_positive,
        tags=tags,
        comment=comment,
    )
    db.add(review)
    try:
        await db.commit()
        await db.refresh(review)
    except IntegrityError as e:
        await db.rollback()
        raise AppException(
            code="REVIEW_ALREADY_SUBMITTED",
            detail="이미 후기를 작성했습니다.",
            status_code=409,
        ) from e
    return review
