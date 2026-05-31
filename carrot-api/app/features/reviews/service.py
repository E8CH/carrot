from sqlalchemy.ext.asyncio import AsyncSession

from app.features.posts import repository as posts_repo
from app.features.reviews import repository
from app.features.reviews.schemas import CreateReviewRequest, ReviewResponse
from app.features.users import repository as users_repo
from app.shared.exceptions import AppException


async def submit_review(
    db: AsyncSession,
    writer_email: str,
    request: CreateReviewRequest,
) -> ReviewResponse:
    post = await posts_repo.get_post_by_id(db, request.post_id)
    if post is None:
        raise AppException(code="POST_NOT_FOUND", detail="게시글을 찾을 수 없습니다.", status_code=404)
    if post.status != '거래완료':
        raise AppException(
            code="TRADE_NOT_COMPLETED",
            detail="거래완료된 게시글에만 후기를 작성할 수 있습니다.",
            status_code=422,
        )

    seller_email = post.seller_email
    buyer_email = post.buyer_email
    if writer_email not in (seller_email, buyer_email):
        raise AppException(
            code="REVIEW_NOT_ELIGIBLE",
            detail="해당 거래의 판매자 또는 구매자만 후기를 작성할 수 있습니다.",
            status_code=403,
        )

    existing = await repository.get_review_by_post_writer(db, request.post_id, writer_email)
    if existing:
        raise AppException(
            code="REVIEW_ALREADY_SUBMITTED",
            detail="이미 후기를 작성했습니다.",
            status_code=409,
        )

    target_email = buyer_email if writer_email == seller_email else seller_email

    review = await repository.create_review(
        db,
        post_id=request.post_id,
        writer_email=writer_email,
        target_email=target_email,
        is_positive=request.is_positive,
        tags=request.tags,
        comment=request.comment,
    )
    delta = 1.0 if request.is_positive else -1.0
    try:
        await users_repo.update_manner_temp(db, target_email, delta)
    except Exception:
        pass

    return ReviewResponse(
        id=review.id,
        post_id=review.post_id,
        writer_email=review.writer_email,
        target_email=review.target_email,
        is_positive=review.is_positive,
        tags=review.tags,
        comment=review.comment,
        created_at=review.created_at,
    )
