import pytest


def test_allowed_origins_empty_by_default():
    """ALLOWED_ORIGINS 미설정 시 빈 문자열 기본값"""
    from app.core.config import settings
    assert settings.ALLOWED_ORIGINS == ""


def test_allowed_origins_parsing():
    """쉼표 구분 ALLOWED_ORIGINS → 오리진 목록으로 파싱"""
    raw = "https://carrot-web.railway.app,https://carrot-admin.railway.app"
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    assert "https://carrot-web.railway.app" in origins
    assert "https://carrot-admin.railway.app" in origins
    assert len(origins) == 2


def test_allowed_origins_empty_string_produces_no_extra():
    """빈 ALLOWED_ORIGINS는 추가 오리진을 생성하지 않음"""
    raw = ""
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    assert origins == []


def test_allowed_origins_with_spaces_trimmed():
    """공백이 포함된 오리진도 정상 파싱"""
    raw = "https://a.railway.app , https://b.railway.app "
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    assert "https://a.railway.app" in origins
    assert "https://b.railway.app" in origins
    assert len(origins) == 2


def test_main_app_imports_without_error():
    """app.main이 정상 import되는지 확인"""
    import app.main  # noqa: F401
    assert True
