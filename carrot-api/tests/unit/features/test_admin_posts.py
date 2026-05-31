import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.features.admin.schemas import AdminPostItem, AdminPostsResponse
from app.shared.exceptions import AppException


def make_admin_dep():
    return {"sub": "admin@example.com", "role": "admin"}


def make_post(post_id: int = 1, status: str = "판매중"):
    post = MagicMock()
    post.id = post_id
    post.title = f"테스트 게시글 {post_id}"
    post.seller_email = "seller@example.com"
    post.price = 10000
    post.is_free = False
    post.status = status
    post.created_at = datetime(2026, 5, 30, tzinfo=timezone.utc)
    post.photos = []
    return post


@pytest.mark.asyncio
async def test_get_admin_posts_all():
    """관리자 전체 게시글 조회 성공"""
    from app.features.admin.router import get_admin_posts
    db = AsyncMock()
    posts = [make_post(1, "판매중"), make_post(2, "거래완료")]

    with patch(
        "app.features.admin.router.admin_repo.get_all_posts",
        new=AsyncMock(return_value=(posts, 2)),
    ):
        result = await get_admin_posts(None, make_admin_dep(), db)

    assert isinstance(result, AdminPostsResponse)
    assert result.total == 2
    assert result.items[0].id == 1
    assert result.items[1].status == "거래완료"


@pytest.mark.asyncio
async def test_get_admin_posts_status_filter():
    """상태 필터 적용 - 판매중만"""
    from app.features.admin.router import get_admin_posts
    db = AsyncMock()
    posts = [make_post(1, "판매중")]

    with patch(
        "app.features.admin.router.admin_repo.get_all_posts",
        new=AsyncMock(return_value=(posts, 1)),
    ):
        result = await get_admin_posts("판매중", make_admin_dep(), db)

    assert result.total == 1
    assert result.items[0].status == "판매중"


@pytest.mark.asyncio
async def test_admin_delete_post_not_found():
    """존재하지 않는 게시글 → POST_NOT_FOUND 404"""
    from app.features.admin.router import admin_delete_post
    db = AsyncMock()

    with patch(
        "app.features.admin.router.admin_repo.get_post_by_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(AppException) as exc_info:
            await admin_delete_post(999, make_admin_dep(), db)

    assert exc_info.value.code == "POST_NOT_FOUND"
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_admin_delete_post_success():
    """게시글 강제삭제 성공 (이미지 없음)"""
    from app.features.admin.router import admin_delete_post
    db = AsyncMock()
    post = make_post(1)
    post.photos = []

    with patch(
        "app.features.admin.router.admin_repo.get_post_by_id",
        new=AsyncMock(return_value=post),
    ), patch(
        "app.features.admin.router.posts_repo.delete_post_by_id",
        new=AsyncMock(),
    ) as mock_delete:
        await admin_delete_post(1, make_admin_dep(), db)

    mock_delete.assert_called_once_with(db, 1)


@pytest.mark.asyncio
async def test_admin_delete_post_with_photos():
    """게시글 강제삭제 — Supabase Storage 먼저 삭제 후 DB 삭제"""
    from app.features.admin.router import admin_delete_post
    db = AsyncMock()
    post = make_post(1)
    post.photos = [
        "https://abc.supabase.co/storage/v1/object/public/posts/seller@example.com/img1.jpg",
    ]

    mock_supabase = MagicMock()
    mock_bucket = MagicMock()
    mock_supabase.storage.from_.return_value = mock_bucket

    with patch(
        "app.features.admin.router.admin_repo.get_post_by_id",
        new=AsyncMock(return_value=post),
    ), patch(
        "app.features.admin.router.posts_repo.delete_post_by_id",
        new=AsyncMock(),
    ) as mock_delete, patch(
        "app.features.admin.router._supabase",
        mock_supabase,
    ):
        await admin_delete_post(1, make_admin_dep(), db)

    mock_supabase.storage.from_.assert_called_once_with("posts")
    mock_bucket.remove.assert_called_once_with(["seller@example.com/img1.jpg"])
    mock_delete.assert_called_once_with(db, 1)
