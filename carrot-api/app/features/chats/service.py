from sqlalchemy.ext.asyncio import AsyncSession

from app.features.chats import repository
from app.features.chats.schemas import ChatRoomListItem, ChatRoomResponse, MessageResponse, UnreadCountResponse
from app.features.posts import repository as posts_repository
from app.shared.exceptions import AppException


async def get_unread_count(db: AsyncSession, user_email: str) -> UnreadCountResponse:
    count = await repository.get_unread_count(db, user_email)
    return UnreadCountResponse(count=count)


async def mark_room_as_read(db: AsyncSession, room_id: str, user_email: str) -> None:
    await repository.mark_room_as_read(db, room_id, user_email)


async def list_chat_rooms(db: AsyncSession, user_email: str) -> list[ChatRoomListItem]:
    rows = await repository.get_chat_rooms(db, user_email)
    result = []
    for msg, photos, unread_count in rows:
        opponent_email = msg.buyer_email if user_email == msg.seller_email else msg.seller_email
        result.append(ChatRoomListItem(
            room_id=msg.room_id,
            post_id=msg.post_id,
            post_thumbnail=photos[0] if photos else None,
            opponent_email=opponent_email,
            seller_email=msg.seller_email,
            buyer_email=msg.buyer_email,
            last_message=msg.message,
            last_sent_at=msg.sent_at,
            unread_count=unread_count or 0,
        ))
    return result


async def create_or_get_chat_room(
    db: AsyncSession,
    buyer_email: str,
    post_id: int,
) -> ChatRoomResponse:
    post = await posts_repository.get_post_by_id(db, post_id)
    if post is None:
        raise AppException(code="POST_NOT_FOUND", detail="게시글을 찾을 수 없습니다.", status_code=404)
    if post.seller_email == buyer_email:
        raise AppException(
            code="SELF_CHAT_FORBIDDEN",
            detail="본인 게시글에는 채팅할 수 없습니다.",
            status_code=403,
        )
    room_id = await repository.get_or_create_room(db, post_id, buyer_email)
    return ChatRoomResponse(
        room_id=room_id,
        post_id=post_id,
        seller_email=post.seller_email,
        buyer_email=buyer_email,
    )


async def send_message(
    db: AsyncSession,
    room_id: str,
    sender_email: str,
    post_id: int,
    message: str,
) -> MessageResponse:
    existing = await repository.get_room_context(db, room_id)
    if existing:
        seller_email = existing.seller_email
        buyer_email = existing.buyer_email
    else:
        post = await posts_repository.get_post_by_id(db, post_id)
        if post is None:
            raise AppException(code="POST_NOT_FOUND", detail="게시글을 찾을 수 없습니다.", status_code=404)
        seller_email = post.seller_email
        if sender_email == seller_email:
            raise AppException(
                code="SELF_CHAT_FORBIDDEN",
                detail="본인 게시글에는 채팅할 수 없습니다.",
                status_code=403,
            )
        buyer_email = sender_email

    if sender_email not in (seller_email, buyer_email):
        raise AppException(code="FORBIDDEN", detail="채팅방 참여자가 아닙니다.", status_code=403)

    msg = await repository.create_message(db, room_id, seller_email, buyer_email, post_id, message, sender_email)
    return MessageResponse.model_validate(msg)


async def get_chat_messages(
    db: AsyncSession,
    room_id: str,
    sender_email: str,
    after_id: int | None = None,
) -> list[MessageResponse]:
    existing = await repository.get_room_context(db, room_id)
    if existing and sender_email not in (existing.seller_email, existing.buyer_email):
        raise AppException(code="FORBIDDEN", detail="채팅방 참여자가 아닙니다.", status_code=403)
    messages = await repository.get_messages(db, room_id, after_id)
    return [MessageResponse.model_validate(m) for m in messages]
