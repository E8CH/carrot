import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.features.posts.schemas import MyPostsResponse
from app.features.posts.service import get_liked_posts


def make_liked_post(post_id: int = 1, status: str = "판매중", photos=None):
    post = MagicMock()
    post.id = post_id
    post.title = f"찜한 게시글 {post_id}"
    post.price = 5000
    post.is_free = False
    post.status = status
    post.photos = photos if photos is not None else ["https://example.com/img.jpg"]
    post.is_draft = False
    post.created_at = datetime(2026, 5, 30, 9, 0, 0, tzinfo=timezone.utc)
    return post


@pytest.mark.asyncio
async def test_get_liked_posts_returns_list():
    """찜한 게시글 목록 정상 반환"""
    db = AsyncMock()
    posts = [
        (make_liked_post(1, "판매중"), 3, 1),
        (make_liked_post(2, "거래완료"), 0, 0),
    ]

    with patch("app.features.posts.service.repository.get_liked_posts", new=AsyncMock(return_value=(posts, 2))):
        result = await get_liked_posts(db, "user@example.com")

    assert isinstance(result, MyPostsResponse)
    assert result.total == 2
    assert len(result.items) == 2
    assert result.items[0].id == 1
    assert result.items[0].like_count == 3
    assert result.items[0].thumbnail == "https://example.com/img.jpg"
    assert result.items[1].status == "거래완료"


@pytest.mark.asyncio
async def test_get_liked_posts_empty():
    """찜한 게시글 없을 때 items=[], total=0"""
    db = AsyncMock()

    with patch("app.features.posts.service.repository.get_liked_posts", new=AsyncMock(return_value=([], 0))):
        result = await get_liked_posts(db, "user@example.com")

    assert result.total == 0
    assert result.items == []


@pytest.mark.asyncio
async def test_get_liked_posts_thumbnail_fallback():
    """photos=[] → thumbnail=None"""
    db = AsyncMock()
    post = make_liked_post(1, photos=[])

    with patch("app.features.posts.service.repository.get_liked_posts", new=AsyncMock(return_value=([(post, 0, 0)], 1))):
        result = await get_liked_posts(db, "user@example.com")

    assert result.items[0].thumbnail is None


@pytest.mark.asyncio
async def test_get_liked_posts_passes_user_email():
    """repository에 user_email이 정확히 전달됨"""
    db = AsyncMock()

    with patch("app.features.posts.service.repository.get_liked_posts", new=AsyncMock(return_value=([], 0))) as mock_repo:
        await get_liked_posts(db, "test@example.com")

    mock_repo.assert_awaited_once_with(db, "test@example.com")
