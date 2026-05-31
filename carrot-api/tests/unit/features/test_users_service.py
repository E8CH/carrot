import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.features.users.schemas import LoginRequest, RegisterRequest, AuthResponse
from app.features.users.service import login, register
from app.shared.exceptions import AppException


def make_register_request(**overrides):
    defaults = dict(
        email="test@example.com",
        password="password123",
        address="서울시 강남구",
        phone="010-1234-5678",
    )
    defaults.update(overrides)
    return RegisterRequest(**defaults)


def make_mock_user(email="test@example.com"):
    user = MagicMock()
    user.id = 1
    user.email = email
    user.address = "서울시 강남구"
    user.phone = "010-1234-5678"
    user.role = "user"
    user.is_active = True
    user.manner_temp = 36.5
    user.created_at = datetime(2026, 5, 29, tzinfo=timezone.utc)
    return user


@pytest.mark.asyncio
async def test_register_success():
    """정상 회원가입: AuthResponse 반환, role=user, manner_temp=36.5"""
    db = AsyncMock()
    request = make_register_request()
    mock_user = make_mock_user()

    with (
        patch("app.features.users.service.repository.get_user_by_email", new=AsyncMock(return_value=None)),
        patch("app.features.users.service.repository.create_user", new=AsyncMock(return_value=mock_user)),
        patch("app.features.users.service.hash_password", return_value="hashed_pw"),
        patch("app.features.users.service.create_access_token", return_value="jwt_token"),
    ):
        result = await register(db, request)

    assert isinstance(result, AuthResponse)
    assert result.access_token == "jwt_token"
    assert result.token_type == "bearer"
    assert result.user.email == "test@example.com"
    assert result.user.role == "user"
    assert result.user.manner_temp == 36.5


@pytest.mark.asyncio
async def test_register_duplicate_email_raises_exception():
    """중복 이메일: EMAIL_ALREADY_EXISTS 예외, HTTP 409"""
    db = AsyncMock()
    request = make_register_request()
    existing_user = make_mock_user()

    with patch("app.features.users.service.repository.get_user_by_email", new=AsyncMock(return_value=existing_user)):
        with pytest.raises(AppException) as exc_info:
            await register(db, request)

    assert exc_info.value.code == "EMAIL_ALREADY_EXISTS"
    assert exc_info.value.status_code == 409
    assert "이미 사용 중인 이메일" in exc_info.value.detail


def test_register_request_password_too_short():
    """비밀번호 8자 미만: Pydantic ValidationError"""
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        RegisterRequest(
            email="test@example.com",
            password="short",  # 5자
            address="서울",
            phone="010-0000-0000",
        )

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("password",) for e in errors)


def test_register_request_invalid_email():
    """유효하지 않은 이메일: Pydantic ValidationError"""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        RegisterRequest(
            email="not-an-email",
            password="password123",
            address="서울",
            phone="010-0000-0000",
        )


@pytest.mark.asyncio
async def test_register_calls_hash_password():
    """hash_password가 실제 호출되는지 확인"""
    db = AsyncMock()
    request = make_register_request()
    mock_user = make_mock_user()

    with (
        patch("app.features.users.service.repository.get_user_by_email", new=AsyncMock(return_value=None)),
        patch("app.features.users.service.repository.create_user", new=AsyncMock(return_value=mock_user)) as mock_create,
        patch("app.features.users.service.hash_password", return_value="hashed_pw") as mock_hash,
        patch("app.features.users.service.create_access_token", return_value="jwt_token"),
    ):
        await register(db, request)

    mock_hash.assert_called_once_with("password123")
    mock_create.assert_called_once()
    _, kwargs = mock_create.call_args
    assert kwargs["hashed_password"] == "hashed_pw"


# ─── Login 테스트 ────────────────────────────────────────────────────────────

def make_login_request(**overrides):
    defaults = dict(email="test@example.com", password="password123")
    defaults.update(overrides)
    return LoginRequest(**defaults)


@pytest.mark.asyncio
async def test_login_success():
    """정상 로그인: AuthResponse 반환"""
    db = AsyncMock()
    request = make_login_request()
    mock_user = make_mock_user()

    with (
        patch("app.features.users.service.repository.get_user_by_email", new=AsyncMock(return_value=mock_user)),
        patch("app.features.users.service.verify_password", return_value=True),
        patch("app.features.users.service.create_access_token", return_value="jwt_token"),
    ):
        result = await login(db, request)

    assert isinstance(result, AuthResponse)
    assert result.access_token == "jwt_token"
    assert result.user.email == "test@example.com"


@pytest.mark.asyncio
async def test_login_user_not_found():
    """존재하지 않는 이메일: INVALID_CREDENTIALS (401)"""
    db = AsyncMock()
    request = make_login_request()

    with patch("app.features.users.service.repository.get_user_by_email", new=AsyncMock(return_value=None)):
        with pytest.raises(AppException) as exc_info:
            await login(db, request)

    assert exc_info.value.code == "INVALID_CREDENTIALS"
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_login_wrong_password():
    """비밀번호 불일치: INVALID_CREDENTIALS (401)"""
    db = AsyncMock()
    request = make_login_request()
    mock_user = make_mock_user()

    with (
        patch("app.features.users.service.repository.get_user_by_email", new=AsyncMock(return_value=mock_user)),
        patch("app.features.users.service.verify_password", return_value=False),
    ):
        with pytest.raises(AppException) as exc_info:
            await login(db, request)

    assert exc_info.value.code == "INVALID_CREDENTIALS"
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_login_inactive_account():
    """비활성화 계정: ACCOUNT_INACTIVE (403)"""
    db = AsyncMock()
    request = make_login_request()
    inactive_user = make_mock_user()
    inactive_user.is_active = False

    with (
        patch("app.features.users.service.repository.get_user_by_email", new=AsyncMock(return_value=inactive_user)),
        patch("app.features.users.service.verify_password", return_value=True),
    ):
        with pytest.raises(AppException) as exc_info:
            await login(db, request)

    assert exc_info.value.code == "ACCOUNT_INACTIVE"
    assert exc_info.value.status_code == 403
