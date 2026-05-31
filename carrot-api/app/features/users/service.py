from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.features.users import repository
from app.features.users.schemas import AuthResponse, LoginRequest, RegisterRequest, UserInfo
from app.shared.exceptions import AppException


async def register(db: AsyncSession, request: RegisterRequest) -> AuthResponse:
    existing = await repository.get_user_by_email(db, request.email)
    if existing:
        raise AppException(
            code="EMAIL_ALREADY_EXISTS",
            detail="이미 사용 중인 이메일입니다.",
            status_code=409,
        )

    hashed = hash_password(request.password)
    user = await repository.create_user(
        db,
        email=request.email,
        hashed_password=hashed,
        address=request.address,
        phone=request.phone,
    )

    token = create_access_token({"sub": user.email, "role": user.role})
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserInfo.model_validate(user),
    )


async def login(db: AsyncSession, request: LoginRequest) -> AuthResponse:
    user = await repository.get_user_by_email(db, request.email)
    # is_active를 verify_password 전에 체크하면 타이밍 사이드채널 발생
    # (비활성+올바른 비밀번호 → bcrypt 수행 후 403, 비활성+틀린 비밀번호 → 즉시 401)
    # 대신 verify_password를 항상 실행하고 두 에러를 순서대로 체크한다
    password_ok = user is not None and verify_password(request.password, user.hashed_password)
    if not password_ok:
        raise AppException(
            code="INVALID_CREDENTIALS",
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            status_code=401,
        )
    if not user.is_active:  # type: ignore[union-attr]  # password_ok 보장 시 user != None
        raise AppException(
            code="ACCOUNT_INACTIVE",
            detail="비활성화된 계정입니다.",
            status_code=403,
        )
    token = create_access_token({"sub": user.email, "role": user.role})
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserInfo.model_validate(user),
    )
