import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.features.posts.schemas import PurchasesResponse
from app.features.posts.service import get_my_purchases


def make_completed_post(post_id: int = 1, photos=None):
    post = MagicMock()
    post.id = post_id
    post.title = f"구매 게시글 {post_id}"
    post.price = 15000
    post.is_free = False
    post.status = "거래완료"
    post.photos = photos if photos is not None else ["https://example.com/img.jpg"]
    post.is_draft = False
    post.updated_at = datetime(2026, 5, 30, 10, 0, 0, tzinfo=timezone.utc)
    return post


@pytest.mark.asyncio
async def test_get_my_purchases_returns_completed_trades():
    """거래완료 목록 정상 반환"""
    db = AsyncMock()
    posts = [make_completed_post(1), make_completed_post(2)]

    with patch("app.features.posts.service.repository.get_my_purchases", new=AsyncMock(return_value=(posts, 2))):
        result = await get_my_purchases(db, "buyer@example.com")

    assert isinstance(result, PurchasesResponse)
    assert result.total == 2
    assert len(result.items) == 2
    assert result.items[0].id == 1
    assert result.items[0].title == "구매 게시글 1"
    assert result.items[0].thumbnail == "https://example.com/img.jpg"
    assert result.items[0].price == 15000
    assert result.items[0].is_free is False


@pytest.mark.asyncio
async def test_get_my_purchases_empty():
    """구매 게시글 없을 때 items=[], total=0"""
    db = AsyncMock()

    with patch("app.features.posts.service.repository.get_my_purchases", new=AsyncMock(return_value=([], 0))):
        result = await get_my_purchases(db, "buyer@example.com")

    assert result.total == 0
    assert result.items == []


@pytest.mark.asyncio
async def test_get_my_purchases_thumbnail_fallback():
    """photos=[] → thumbnail=None"""
    db = AsyncMock()
    post = make_completed_post(1, photos=[])

    with patch("app.features.posts.service.repository.get_my_purchases", new=AsyncMock(return_value=([post], 1))):
        result = await get_my_purchases(db, "buyer@example.com")

    assert result.items[0].thumbnail is None


@pytest.mark.asyncio
async def test_get_my_purchases_free_post():
    """나눔 게시글: price=None, is_free=True"""
    db = AsyncMock()
    post = make_completed_post(1)
    post.price = None
    post.is_free = True

    with patch("app.features.posts.service.repository.get_my_purchases", new=AsyncMock(return_value=([post], 1))):
        result = await get_my_purchases(db, "buyer@example.com")

    assert result.items[0].price is None
    assert result.items[0].is_free is True


@pytest.mark.asyncio
async def test_get_my_purchases_passes_buyer_email():
    """repository에 buyer_email이 정확히 전달됨"""
    db = AsyncMock()

    with patch("app.features.posts.service.repository.get_my_purchases", new=AsyncMock(return_value=([], 0))) as mock_repo:
        await get_my_purchases(db, "test@example.com")

    mock_repo.assert_awaited_once_with(db, "test@example.com")
