import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.features.reviews.schemas import CreateReviewRequest, ReviewResponse
from app.features.reviews.service import submit_review
from app.shared.exceptions import AppException


def make_completed_post(
    post_id: int = 1,
    seller: str = "seller@example.com",
    buyer: str = "buyer@example.com",
):
    post = MagicMock()
    post.id = post_id
    post.status = "거래완료"
    post.seller_email = seller
    post.buyer_email = buyer
    return post


def make_review(
    post_id: int = 1,
    writer: str = "seller@example.com",
    target: str = "buyer@example.com",
    is_positive: bool = True,
):
    review = MagicMock()
    review.id = 1
    review.post_id = post_id
    review.writer_email = writer
    review.target_email = target
    review.is_positive = is_positive
    review.tags = ["친절해요"]
    review.comment = None
    review.created_at = datetime(2026, 5, 30, tzinfo=timezone.utc)
    return review


@pytest.mark.asyncio
async def test_submit_review_success_seller_to_buyer():
    """판매자가 구매자에게 긍정 후기 → target=buyer, manner_temp +1"""
    db = AsyncMock()
    post = make_completed_post()
    review = make_review()

    with (
        patch("app.features.reviews.service.posts_repo.get_post_by_id", new=AsyncMock(return_value=post)),
        patch("app.features.reviews.service.repository.get_review_by_post_writer", new=AsyncMock(return_value=None)),
        patch("app.features.reviews.service.repository.create_review", new=AsyncMock(return_value=review)),
        patch("app.features.reviews.service.users_repo.update_manner_temp", new=AsyncMock()) as mock_temp,
    ):
        result = await submit_review(
            db, "seller@example.com",
            CreateReviewRequest(post_id=1, is_positive=True, tags=["친절해요"]),
        )

    assert isinstance(result, ReviewResponse)
    assert result.target_email == "buyer@example.com"
    assert result.is_positive is True
    mock_temp.assert_awaited_once_with(db, "buyer@example.com", 1.0)


@pytest.mark.asyncio
async def test_submit_review_success_buyer_to_seller():
    """구매자가 판매자에게 부정 후기 → target=seller, manner_temp -1"""
    db = AsyncMock()
    post = make_completed_post()
    review = make_review(writer="buyer@example.com", target="seller@example.com", is_positive=False)

    with (
        patch("app.features.reviews.service.posts_repo.get_post_by_id", new=AsyncMock(return_value=post)),
        patch("app.features.reviews.service.repository.get_review_by_post_writer", new=AsyncMock(return_value=None)),
        patch("app.features.reviews.service.repository.create_review", new=AsyncMock(return_value=review)),
        patch("app.features.reviews.service.users_repo.update_manner_temp", new=AsyncMock()) as mock_temp,
    ):
        result = await submit_review(
            db, "buyer@example.com",
            CreateReviewRequest(post_id=1, is_positive=False, tags=[]),
        )

    assert result.target_email == "seller@example.com"
    assert result.is_positive is False
    mock_temp.assert_awaited_once_with(db, "seller@example.com", -1.0)


@pytest.mark.asyncio
async def test_submit_review_already_submitted():
    """이미 후기를 작성한 경우 → REVIEW_ALREADY_SUBMITTED (409)"""
    db = AsyncMock()
    post = make_completed_post()
    existing_review = MagicMock()

    with (
        patch("app.features.reviews.service.posts_repo.get_post_by_id", new=AsyncMock(return_value=post)),
        patch("app.features.reviews.service.repository.get_review_by_post_writer", new=AsyncMock(return_value=existing_review)),
    ):
        with pytest.raises(AppException) as exc_info:
            await submit_review(
                db, "seller@example.com",
                CreateReviewRequest(post_id=1, is_positive=True),
            )

    assert exc_info.value.code == "REVIEW_ALREADY_SUBMITTED"
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_submit_review_not_eligible():
    """거래 당사자가 아닌 사람의 후기 → REVIEW_NOT_ELIGIBLE (403)"""
    db = AsyncMock()
    post = make_completed_post()

    with patch("app.features.reviews.service.posts_repo.get_post_by_id", new=AsyncMock(return_value=post)):
        with pytest.raises(AppException) as exc_info:
            await submit_review(
                db, "stranger@example.com",
                CreateReviewRequest(post_id=1, is_positive=True),
            )

    assert exc_info.value.code == "REVIEW_NOT_ELIGIBLE"
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_submit_review_post_not_completed():
    """거래완료 아닌 게시글에 후기 → TRADE_NOT_COMPLETED (422)"""
    db = AsyncMock()
    post = make_completed_post()
    post.status = "판매중"

    with patch("app.features.reviews.service.posts_repo.get_post_by_id", new=AsyncMock(return_value=post)):
        with pytest.raises(AppException) as exc_info:
            await submit_review(
                db, "seller@example.com",
                CreateReviewRequest(post_id=1, is_positive=True),
            )

    assert exc_info.value.code == "TRADE_NOT_COMPLETED"
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_submit_review_post_not_found():
    """존재하지 않는 게시글 → POST_NOT_FOUND (404)"""
    db = AsyncMock()

    with patch("app.features.reviews.service.posts_repo.get_post_by_id", new=AsyncMock(return_value=None)):
        with pytest.raises(AppException) as exc_info:
            await submit_review(
                db, "seller@example.com",
                CreateReviewRequest(post_id=999, is_positive=True),
            )

    assert exc_info.value.code == "POST_NOT_FOUND"
    assert exc_info.value.status_code == 404
