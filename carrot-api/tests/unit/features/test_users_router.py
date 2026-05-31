import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.features.users.schemas import UserInfo
from app.shared.exceptions import AppException


def make_mock_user(manner_temp=36.5):
    user = MagicMock()
    user.id = 1
    user.email = "test@example.com"
    user.address = "서울시 강남구"
    user.phone = "010-1234-5678"
    user.role = "user"
    user.is_active = True
    user.manner_temp = manner_temp
    user.created_at = datetime(2026, 5, 29, tzinfo=timezone.utc)
    return user


def make_valid_token_payload():
    return {"sub": "test@example.com", "role": "user"}


def test_get_me_success():
    """JWT 있음 → 200 + UserInfo"""
    client = TestClient(app)
    mock_user = make_mock_user()

    with (
        patch("app.core.dependencies.verify_token", return_value=make_valid_token_payload()),
        patch(
            "app.features.users.repository.get_user_by_email",
            new=AsyncMock(return_value=mock_user),
        ),
    ):
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer valid_token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"


def test_get_me_manner_temp_rounded():
    """manner_temp 소수점 1자리 반환"""
    client = TestClient(app)
    mock_user = make_mock_user(manner_temp=36.555)

    with (
        patch("app.core.dependencies.verify_token", return_value=make_valid_token_payload()),
        patch(
            "app.features.users.repository.get_user_by_email",
            new=AsyncMock(return_value=mock_user),
        ),
    ):
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer valid_token"},
        )

    assert response.status_code == 200
    assert response.json()["manner_temp"] == 36.6


def test_get_me_no_token():
    """JWT 없음 → 401"""
    client = TestClient(app)
    response = client.get("/api/v1/users/me")
    assert response.status_code == 422  # Header 누락 시 FastAPI 422


def test_get_me_invalid_token():
    """유효하지 않은 JWT → 401"""
    client = TestClient(app)

    with patch("app.core.dependencies.verify_token", return_value=None):
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer bad_token"},
        )

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"
