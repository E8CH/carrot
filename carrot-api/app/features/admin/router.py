from typing import Literal

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import create_client

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.security import create_access_token, hash_password, verify_password
from app.features.admin import repository as admin_repo
from app.features.admin.schemas import (
    AdminChatMessageItem,
    AdminChatMessagesResponse,
    AdminChatRoomItem,
    AdminChatRoomsResponse,
    AdminLoginRequest,
    AdminPostItem,
    AdminPostsResponse,
    AdminRegisterRequest,
    AdminUserItem,
    AdminUsersResponse,
    AdminUserStatusRequest,
)
from app.features.posts import repository as posts_repo
from app.features.users import repository as users_repo
from app.features.users.models import User
from app.features.users.schemas import AuthResponse, UserInfo
from app.shared.exceptions import AppException

router = APIRouter()

_supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
_BUCKET = "posts"


@router.post("/register", response_model=AuthResponse, status_code=201)
async def admin_register(
    request: AdminRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    existing = await users_repo.get_user_by_email(db, request.email)
    if existing:
        raise AppException(
            code="EMAIL_ALREADY_EXISTS",
            detail="이미 사용 중인 이메일입니다.",
            status_code=409,
        )

    hashed = hash_password(request.password)
    user = User(
        email=request.email,
        hashed_password=hashed,
        address="",
        phone="",
        role="admin",
    )
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise AppException(
            code="EMAIL_ALREADY_EXISTS",
            detail="이미 사용 중인 이메일입니다.",
            status_code=409,
        )

    token = create_access_token({"sub": user.email, "role": user.role})
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserInfo.model_validate(user),
    )


@router.post("/login", response_model=AuthResponse)
async def admin_login(
    request: AdminLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    user = await users_repo.get_user_by_email(db, request.email)
    password_ok = user is not None and verify_password(request.password, user.hashed_password)
    if not password_ok:
        raise AppException(
            code="INVALID_CREDENTIALS",
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            status_code=401,
        )
    if not user.is_active:  # type: ignore[union-attr]
        raise AppException(
            code="ACCOUNT_INACTIVE",
            detail="비활성화된 계정입니다.",
            status_code=403,
        )
    if user.role != "admin":  # type: ignore[union-attr]
        raise AppException(
            code="ADMIN_REQUIRED",
            detail="관리자 권한이 없습니다.",
            status_code=403,
        )

    token = create_access_token({"sub": user.email, "role": user.role})
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserInfo.model_validate(user),
    )


@router.get("/users", response_model=AdminUsersResponse)
async def get_admin_users(
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> AdminUsersResponse:
    rows, total = await admin_repo.get_all_users(db)
    items = [
        AdminUserItem(
            email=user.email,
            created_at=user.created_at,
            manner_temp=user.manner_temp,
            post_count=post_count,
            is_active=user.is_active,
        )
        for user, post_count in rows
    ]
    return AdminUsersResponse(items=items, total=total)


@router.patch("/users/{email}/status", response_model=AdminUserItem)
async def update_user_status(
    email: str,
    request: AdminUserStatusRequest,
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> AdminUserItem:
    user = await users_repo.get_user_by_email(db, email)
    if not user:
        raise AppException(
            code="USER_NOT_FOUND",
            detail="사용자를 찾을 수 없습니다.",
            status_code=404,
        )
    user.is_active = request.is_active
    await db.commit()
    await db.refresh(user)
    return AdminUserItem(
        email=user.email,
        created_at=user.created_at,
        manner_temp=user.manner_temp,
        post_count=0,
        is_active=user.is_active,
    )


PostStatus = Literal["판매중", "예약중", "거래완료"]


@router.get("/posts", response_model=AdminPostsResponse)
async def get_admin_posts(
    status: PostStatus | None = Query(default=None),
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> AdminPostsResponse:
    posts, total = await admin_repo.get_all_posts(db, status)
    items = [
        AdminPostItem(
            id=post.id,
            title=post.title,
            seller_email=post.seller_email,
            price=post.price,
            is_free=post.is_free,
            status=post.status,
            created_at=post.created_at,
        )
        for post in posts
    ]
    return AdminPostsResponse(items=items, total=total)


@router.delete("/posts/{post_id}", status_code=204)
async def admin_delete_post(
    post_id: int = Path(ge=1),
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    post = await admin_repo.get_post_by_id(db, post_id)
    if post is None:
        raise AppException(code="POST_NOT_FOUND", detail="게시글을 찾을 수 없습니다.", status_code=404)
    photos = list(post.photos or [])
    if photos:
        file_paths = [
            url.split(f"/storage/v1/object/public/{_BUCKET}/")[-1]
            for url in photos
            if f"/storage/v1/object/public/{_BUCKET}/" in url
        ]
        if file_paths:
            try:
                _supabase.storage.from_(_BUCKET).remove(file_paths)
            except Exception:
                pass
    await posts_repo.delete_post_by_id(db, post_id)


@router.get("/chats", response_model=AdminChatRoomsResponse)
async def get_admin_chats(
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> AdminChatRoomsResponse:
    rows, total = await admin_repo.get_all_chat_rooms(db)
    items = [
        AdminChatRoomItem(
            room_id=row.room_id,
            seller_email=row.seller_email,
            buyer_email=row.buyer_email,
            post_title=row.post_title,
            message_count=row.message_count,
            last_message_at=row.last_message_at,
        )
        for row in rows
    ]
    return AdminChatRoomsResponse(items=items, total=total)


_UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"


@router.get("/chats/{room_id}/messages", response_model=AdminChatMessagesResponse)
async def get_admin_chat_messages(
    room_id: str = Path(..., pattern=_UUID_PATTERN),
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> AdminChatMessagesResponse:
    messages = await admin_repo.get_room_messages_admin(db, room_id)
    items = [
        AdminChatMessageItem(
            id=msg.id,
            sender_email=msg.sender_email,
            message=msg.message,
            sent_at=msg.sent_at,
        )
        for msg in messages
    ]
    return AdminChatMessagesResponse(room_id=room_id, items=items)
