import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.features.admin.schemas import AdminLoginRequest, AdminRegisterRequest
from app.features.users.schemas import AuthResponse, UserInfo
from app.shared.exceptions import AppException


def make_user_info(email: str = "admin@example.com", role: str = "admin") -> UserInfo:
    return UserInfo(
        id=1,
        email=email,
        address="",
        phone="",
        role=role,
        manner_temp=36.5,
        created_at=datetime(2026, 5, 30, tzinfo=timezone.utc),
    )


def make_admin_user(email: str = "admin@example.com", role: str = "admin", is_active: bool = True):
    user = MagicMock()
    user.id = 1
    user.email = email
    user.hashed_password = "hashed"
    user.address = ""
    user.phone = ""
    user.role = role
    user.is_active = is_active
    user.manner_temp = 36.5
    user.created_at = datetime(2026, 5, 30, tzinfo=timezone.utc)
    user.updated_at = datetime(2026, 5, 30, tzinfo=timezone.utc)
    return user


@pytest.mark.asyncio
async def test_admin_register_success():
    """관리자 등록 성공 → role=admin JWT 반환"""
    from app.features.admin.router import admin_register
    db = AsyncMock()
    request = AdminRegisterRequest(email="admin@example.com", password="password123")
    user = make_admin_user()

    with (
        patch("app.features.admin.router.users_repo.get_user_by_email", new=AsyncMock(return_value=None)),
        patch("app.features.admin.router.hash_password", return_value="hashed"),
        patch("app.features.admin.router.create_access_token", return_value="test_token"),
        patch("app.features.admin.router.UserInfo.model_validate", return_value=make_user_info()),
    ):
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        db.add = MagicMock()
        result = await admin_register(request, db)

    assert result.access_token == "test_token"


@pytest.mark.asyncio
async def test_admin_register_duplicate_email():
    """중복 이메일 → EMAIL_ALREADY_EXISTS 409"""
    from app.features.admin.router import admin_register
    db = AsyncMock()
    request = AdminRegisterRequest(email="admin@example.com", password="password123")
    existing_user = make_admin_user()

    with patch("app.features.admin.router.users_repo.get_user_by_email", new=AsyncMock(return_value=existing_user)):
        with pytest.raises(AppException) as exc_info:
            await admin_register(request, db)

    assert exc_info.value.code == "EMAIL_ALREADY_EXISTS"
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_admin_login_success():
    """관리자 로그인 성공"""
    from app.features.admin.router import admin_login
    db = AsyncMock()
    request = AdminLoginRequest(email="admin@example.com", password="password123")
    user = make_admin_user(role="admin")

    with (
        patch("app.features.admin.router.users_repo.get_user_by_email", new=AsyncMock(return_value=user)),
        patch("app.features.admin.router.verify_password", return_value=True),
        patch("app.features.admin.router.create_access_token", return_value="admin_token"),
        patch("app.features.admin.router.UserInfo.model_validate", return_value=make_user_info()),
    ):
        result = await admin_login(request, db)

    assert result.access_token == "admin_token"


@pytest.mark.asyncio
async def test_admin_login_not_admin():
    """일반 사용자 로그인 → ADMIN_REQUIRED 403"""
    from app.features.admin.router import admin_login
    db = AsyncMock()
    request = AdminLoginRequest(email="user@example.com", password="password123")
    user = make_admin_user(role="user")

    with (
        patch("app.features.admin.router.users_repo.get_user_by_email", new=AsyncMock(return_value=user)),
        patch("app.features.admin.router.verify_password", return_value=True),
    ):
        with pytest.raises(AppException) as exc_info:
            await admin_login(request, db)

    assert exc_info.value.code == "ADMIN_REQUIRED"
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_admin_login_wrong_password():
    """잘못된 비밀번호 → INVALID_CREDENTIALS 401"""
    from app.features.admin.router import admin_login
    db = AsyncMock()
    request = AdminLoginRequest(email="admin@example.com", password="wrongpassword")
    user = make_admin_user()

    with (
        patch("app.features.admin.router.users_repo.get_user_by_email", new=AsyncMock(return_value=user)),
        patch("app.features.admin.router.verify_password", return_value=False),
    ):
        with pytest.raises(AppException) as exc_info:
            await admin_login(request, db)

    assert exc_info.value.code == "INVALID_CREDENTIALS"
    assert exc_info.value.status_code == 401
