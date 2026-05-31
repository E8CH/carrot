from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.chats.models import ChatMessage
from app.features.posts.models import Post
from app.features.users.models import User


async def get_all_chat_rooms(db: AsyncSession) -> tuple[list, int]:
    stmt = (
        select(
            ChatMessage.room_id,
            ChatMessage.seller_email,
            ChatMessage.buyer_email,
            ChatMessage.post_id,
            func.count(ChatMessage.id).label("message_count"),
            func.max(ChatMessage.sent_at).label("last_message_at"),
            Post.title.label("post_title"),
        )
        .join(Post, Post.id == ChatMessage.post_id)
        .group_by(
            ChatMessage.room_id,
            ChatMessage.seller_email,
            ChatMessage.buyer_email,
            ChatMessage.post_id,
            Post.title,
        )
        .order_by(func.max(ChatMessage.sent_at).desc())
    )
    rows = list((await db.execute(stmt)).all())
    return rows, len(rows)


async def get_room_messages_admin(db: AsyncSession, room_id: str) -> list:
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.room_id == room_id)
        .order_by(ChatMessage.sent_at)
    )
    return list((await db.execute(stmt)).scalars().all())


async def get_all_posts(db: AsyncSession, status: str | None) -> tuple[list, int]:
    filters = [Post.is_draft == False]  # noqa: E712
    if status is not None:
        filters.append(Post.status == status)
    stmt = (
        select(Post)
        .where(*filters)
        .order_by(Post.created_at.desc())
    )
    rows = list((await db.execute(stmt)).scalars().all())
    return rows, len(rows)


async def get_post_by_id(db: AsyncSession, post_id: int) -> Post | None:
    stmt = select(Post).where(Post.id == post_id)
    return (await db.execute(stmt)).scalar_one_or_none()


async def get_all_users(db: AsyncSession) -> tuple[list, int]:
    post_count_sq = (
        select(func.count(Post.id))
        .where(Post.seller_email == User.email, Post.is_draft == False)  # noqa: E712
        .correlate(User)
        .scalar_subquery()
    )
    stmt = (
        select(User, post_count_sq.label("post_count"))
        .order_by(User.created_at.desc())
    )
    rows = (await db.execute(stmt)).all()
    return rows, len(rows)
