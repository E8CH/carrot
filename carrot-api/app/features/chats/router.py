from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.features.chats import service
from app.features.chats.schemas import (
    ChatRoomListItem,
    ChatRoomResponse,
    CreateChatRequest,
    MessageResponse,
    SendMessageRequest,
    UnreadCountResponse,
)
from app.shared.exceptions import AppException

router = APIRouter()


@router.get("/", response_model=list[ChatRoomListItem])
async def list_chats(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ChatRoomListItem]:
    user_email = current_user.get("sub")
    if not user_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return await service.list_chat_rooms(db, user_email)


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UnreadCountResponse:
    user_email = current_user.get("sub")
    if not user_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return await service.get_unread_count(db, user_email)


@router.patch("/{room_id}/read", status_code=204)
async def mark_as_read(
    room_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    user_email = current_user.get("sub")
    if not user_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    await service.mark_room_as_read(db, room_id, user_email)


@router.post("/", response_model=ChatRoomResponse, status_code=200)
async def create_or_get_chat(
    request: CreateChatRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatRoomResponse:
    buyer_email = current_user.get("sub")
    if not buyer_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return await service.create_or_get_chat_room(db, buyer_email, request.post_id)


@router.post("/{room_id}/messages", response_model=MessageResponse, status_code=201)
async def send_message(
    room_id: str,
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    sender_email = current_user.get("sub")
    if not sender_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return await service.send_message(db, room_id, sender_email, request.post_id, request.message)


@router.get("/{room_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    room_id: str,
    after: int | None = Query(default=None, ge=1),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MessageResponse]:
    sender_email = current_user.get("sub")
    if not sender_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return await service.get_chat_messages(db, room_id, sender_email, after)
