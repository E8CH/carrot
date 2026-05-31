from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.features.posts import service as posts_service
from app.features.posts.schemas import MyPostsResponse, PurchasesResponse
from app.features.users import repository, service
from app.features.users.schemas import AuthResponse, LoginRequest, RegisterRequest, UserInfo
from app.shared.exceptions import AppException

_VALID_STATUSES = frozenset({"판매중", "예약중", "거래완료"})

# /auth 접두사 — 인증 엔드포인트
router = APIRouter()

# /users 접두사 — 회원 리소스 엔드포인트
users_router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    return await service.register(db, request)


@router.post("/login", response_model=AuthResponse, status_code=200)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    return await service.login(db, request)


@users_router.get("/me", response_model=UserInfo)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserInfo:
    email = current_user.get("sub")
    if not email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    user = await repository.get_user_by_email(db, email)
    if not user:
        raise AppException(code="USER_NOT_FOUND", detail="사용자를 찾을 수 없습니다.", status_code=404)
    # ORM 객체 변이 없이 UserInfo 생성 후 manner_temp 반올림 적용
    info = UserInfo.model_validate(user)
    info.manner_temp = round(info.manner_temp, 1)
    return info


@users_router.get("/me/posts", response_model=MyPostsResponse)
async def get_my_posts(
    status: str | None = Query(default=None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MyPostsResponse:
    email = current_user.get("sub")
    if not email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    if status is not None and status not in _VALID_STATUSES:
        raise AppException(code="INVALID_STATUS", detail="유효하지 않은 상태값입니다.", status_code=422)
    return await posts_service.get_my_posts(db, email, status)


@users_router.get("/me/purchases", response_model=PurchasesResponse)
async def get_my_purchases(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PurchasesResponse:
    email = current_user.get("sub")
    if not email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return await posts_service.get_my_purchases(db, email)


@users_router.get("/me/likes", response_model=MyPostsResponse)
async def get_my_likes(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MyPostsResponse:
    email = current_user.get("sub")
    if not email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return await posts_service.get_liked_posts(db, email)
