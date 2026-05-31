import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.features.admin.schemas import AdminUsersResponse, AdminUserItem
from app.shared.exceptions import AppException


def make_admin_dep():
    return {"sub": "admin@example.com", "role": "admin"}


def make_user_row(email: str = "user@example.com", is_active: bool = True, post_count: int = 3):
    user = MagicMock()
    user.email = email
    user.is_active = is_active
    user.manner_temp = 36.5
    user.created_at = datetime(2026, 5, 30, tzinfo=timezone.utc)
    return (user, post_count)


@pytest.mark.asyncio
async def test_get_admin_users_success():
    """관리자 회원 목록 조회 성공"""
    from app.features.admin.router import get_admin_users
    db = AsyncMock()
    rows = [make_user_row("a@test.com", True, 2), make_user_row("b@test.com", False, 0)]

    with patch("app.features.admin.router.admin_repo.get_all_users", new=AsyncMock(return_value=(rows, 2))):
        result = await get_admin_users(make_admin_dep(), db)

    assert isinstance(result, AdminUsersResponse)
    assert result.total == 2
    assert result.items[0].email == "a@test.com"
    assert result.items[0].post_count == 2
    assert result.items[1].is_active is False


@pytest.mark.asyncio
async def test_update_user_status_deactivate():
    """회원 비활성화 성공"""
    from app.features.admin.router import update_user_status
    from app.features.admin.schemas import AdminUserStatusRequest
    db = AsyncMock()
    user = MagicMock()
    user.email = "user@example.com"
    user.is_active = True
    user.manner_temp = 36.5
    user.created_at = datetime(2026, 5, 30, tzinfo=timezone.utc)

    with patch("app.features.admin.router.users_repo.get_user_by_email", new=AsyncMock(return_value=user)):
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        result = await update_user_status(
            "user@example.com",
            AdminUserStatusRequest(is_active=False),
            make_admin_dep(),
            db,
        )

    assert user.is_active is False
    assert result.email == "user@example.com"


@pytest.mark.asyncio
async def test_update_user_status_not_found():
    """존재하지 않는 회원 → USER_NOT_FOUND 404"""
    from app.features.admin.router import update_user_status
    from app.features.admin.schemas import AdminUserStatusRequest
    db = AsyncMock()

    with patch("app.features.admin.router.users_repo.get_user_by_email", new=AsyncMock(return_value=None)):
        with pytest.raises(AppException) as exc_info:
            await update_user_status(
                "unknown@example.com",
                AdminUserStatusRequest(is_active=False),
                make_admin_dep(),
                db,
            )

    assert exc_info.value.code == "USER_NOT_FOUND"
    assert exc_info.value.status_code == 404
