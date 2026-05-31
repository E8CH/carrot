import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.features.posts.schemas import MyPostsResponse, PostListItem
from app.features.posts.service import get_my_posts


def make_mock_post(post_id: int = 1, status: str = "판매중", photos=None):
    post = MagicMock()
    post.id = post_id
    post.title = f"게시글 {post_id}"
    post.price = 10000
    post.is_free = False
    post.status = status
    post.photos = photos if photos is not None else ["https://example.com/photo.jpg"]
    post.is_draft = False
    post.created_at = datetime(2026, 5, 30, 12, 0, 0, tzinfo=timezone.utc)
    return post


@pytest.mark.asyncio
async def test_get_my_posts_all():
    """status=None → 전체 목록 반환"""
    db = AsyncMock()
    posts = [
        (make_mock_post(1, "판매중"), 2, 3),
        (make_mock_post(2, "거래완료"), 0, 1),
    ]

    with patch("app.features.posts.service.repository.get_my_posts", new=AsyncMock(return_value=(posts, 2))):
        result = await get_my_posts(db, "seller@example.com", None)

    assert isinstance(result, MyPostsResponse)
    assert result.total == 2
    assert len(result.items) == 2
    assert result.items[0].id == 1
    assert result.items[0].like_count == 2
    assert result.items[0].chat_count == 3
    assert result.items[1].status == "거래완료"


@pytest.mark.asyncio
async def test_get_my_posts_with_status():
    """status="판매중" → 필터된 목록 반환"""
    db = AsyncMock()
    posts = [(make_mock_post(1, "판매중"), 1, 0)]

    with patch("app.features.posts.service.repository.get_my_posts", new=AsyncMock(return_value=(posts, 1))) as mock_repo:
        result = await get_my_posts(db, "seller@example.com", "판매중")

    assert result.total == 1
    assert result.items[0].status == "판매중"
    mock_repo.assert_awaited_once_with(db, "seller@example.com", "판매중")


@pytest.mark.asyncio
async def test_get_my_posts_empty():
    """게시글 없을 때 items=[], total=0"""
    db = AsyncMock()

    with patch("app.features.posts.service.repository.get_my_posts", new=AsyncMock(return_value=([], 0))):
        result = await get_my_posts(db, "seller@example.com", None)

    assert result.total == 0
    assert result.items == []


@pytest.mark.asyncio
async def test_get_my_posts_thumbnail_fallback():
    """photos=[] → thumbnail=None"""
    db = AsyncMock()
    post = make_mock_post(1, photos=[])
    posts = [(post, 0, 0)]

    with patch("app.features.posts.service.repository.get_my_posts", new=AsyncMock(return_value=(posts, 1))):
        result = await get_my_posts(db, "seller@example.com", None)

    assert result.items[0].thumbnail is None


@pytest.mark.asyncio
async def test_get_my_posts_thumbnail_first_photo():
    """photos 있으면 thumbnail=photos[0]"""
    db = AsyncMock()
    post = make_mock_post(1, photos=["https://cdn.example.com/img1.jpg", "https://cdn.example.com/img2.jpg"])
    posts = [(post, 0, 0)]

    with patch("app.features.posts.service.repository.get_my_posts", new=AsyncMock(return_value=(posts, 1))):
        result = await get_my_posts(db, "seller@example.com", None)

    assert result.items[0].thumbnail == "https://cdn.example.com/img1.jpg"
