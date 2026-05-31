from fastapi import Depends, Header

from app.core.security import verify_token
from app.shared.exceptions import AppException


async def get_current_user(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise AppException(code="UNAUTHORIZED", detail="인증이 필요합니다.", status_code=401)
    token = authorization.removeprefix("Bearer ")
    payload = verify_token(token)
    if not payload:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return payload


async def get_optional_user(authorization: str | None = Header(default=None)) -> dict | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ")
    return verify_token(token)


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise AppException(
            code="ADMIN_REQUIRED", detail="관리자 권한이 없습니다.", status_code=403
        )
    return current_user
