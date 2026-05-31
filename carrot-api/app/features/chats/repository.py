import uuid

from sqlalchemy import distinct, func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.chats.models import ChatMessage
from app.features.posts.models import Post
from app.shared.exceptions import AppException


async def get_or_create_room(db: AsyncSession, post_id: int, buyer_email: str) -> str:
    stmt = (
        select(ChatMessage.room_id)
        .where(ChatMessage.post_id == post_id, ChatMessage.buyer_email == buyer_email)
        .limit(1)
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        return existing
    return str(uuid.uuid4())


async def get_room_context(db: AsyncSession, room_id: str) -> ChatMessage | None:
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.room_id == room_id)
        .order_by(ChatMessage.sent_at)
        .limit(1)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def create_message(
    db: AsyncSession,
    room_id: str,
    seller_email: str,
    buyer_email: str,
    post_id: int,
    message: str,
    sender_email: str,
) -> ChatMessage:
    msg = ChatMessage(
        room_id=room_id,
        seller_email=seller_email,
        buyer_email=buyer_email,
        post_id=post_id,
        message=message,
        sender_email=sender_email,
        is_read=False,
    )
    db.add(msg)
    try:
        await db.commit()
        await db.refresh(msg)
    except IntegrityError as e:
        await db.rollback()
        raise AppException(
            code="MESSAGE_SEND_FAILED",
            detail="메시지 전송에 실패했습니다.",
            status_code=422,
        ) from e
    return msg


async def get_unread_count(db: AsyncSession, user_email: str) -> int:
    stmt = select(func.count(distinct(ChatMessage.room_id))).where(
        or_(
            ChatMessage.seller_email == user_email,
            ChatMessage.buyer_email == user_email,
        ),
        ChatMessage.is_read == False,  # noqa: E712
        ChatMessage.sender_email != user_email,
    )
    return (await db.execute(stmt)).scalar_one()


async def mark_room_as_read(db: AsyncSession, room_id: str, user_email: str) -> None:
    stmt = (
        update(ChatMessage)
        .where(
            ChatMessage.room_id == room_id,
            or_(
                ChatMessage.seller_email == user_email,
                ChatMessage.buyer_email == user_email,
            ),
            ChatMessage.sender_email != user_email,
        )
        .values(is_read=True)
    )
    await db.execute(stmt)
    await db.commit()


async def get_chat_rooms(db: AsyncSession, user_email: str) -> list:
    latest_id_subq = (
        select(
            ChatMessage.room_id,
            func.max(ChatMessage.id).label("max_id"),
        )
        .where(
            or_(
                ChatMessage.seller_email == user_email,
                ChatMessage.buyer_email == user_email,
            )
        )
        .group_by(ChatMessage.room_id)
        .subquery("latest_id")
    )

    unread_subq = (
        select(
            ChatMessage.room_id,
            func.count(ChatMessage.id).label("unread_count"),
        )
        .where(
            or_(
                ChatMessage.seller_email == user_email,
                ChatMessage.buyer_email == user_email,
            ),
            ChatMessage.is_read == False,  # noqa: E712
            ChatMessage.sender_email != user_email,
        )
        .group_by(ChatMessage.room_id)
        .subquery("unread")
    )

    stmt = (
        select(
            ChatMessage,
            Post.photos,
            unread_subq.c.unread_count,
        )
        .join(latest_id_subq, ChatMessage.id == latest_id_subq.c.max_id)
        .join(Post, Post.id == ChatMessage.post_id)
        .outerjoin(unread_subq, unread_subq.c.room_id == ChatMessage.room_id)
        .order_by(ChatMessage.sent_at.desc())
    )

    return list((await db.execute(stmt)).all())


async def get_messages(
    db: AsyncSession,
    room_id: str,
    after_id: int | None = None,
    limit: int = 50,
) -> list[ChatMessage]:
    stmt = select(ChatMessage).where(ChatMessage.room_id == room_id)
    if after_id is not None:
        stmt = stmt.where(ChatMessage.id > after_id)
    stmt = stmt.order_by(ChatMessage.sent_at).limit(limit)
    return list((await db.execute(stmt)).scalars().all())
