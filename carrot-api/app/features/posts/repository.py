from datetime import datetime, timezone

from sqlalchemy import delete, distinct, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.chats.models import ChatMessage
from app.features.posts.models import Like, Post
from app.features.posts.schemas import CreatePostRequest, SaveDraftRequest, UpdatePostRequest
from app.features.users.models import User
from app.shared.exceptions import AppException


async def get_posts(
    db: AsyncSession, page: int, size: int
) -> tuple[list, int]:
    like_count_sq = (
        select(func.count(Like.id))
        .where(Like.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
    )
    chat_count_sq = (
        select(func.count(ChatMessage.id))
        .where(ChatMessage.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
    )

    stmt = (
        select(
            Post,
            like_count_sq.label("like_count"),
            chat_count_sq.label("chat_count"),
        )
        .where(Post.is_draft == False)  # noqa: E712
        .order_by(Post.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    rows = (await db.execute(stmt)).all()

    total_stmt = select(func.count(Post.id)).where(Post.is_draft == False)  # noqa: E712
    total = (await db.execute(total_stmt)).scalar_one()

    return rows, total


async def get_post_by_id(db: AsyncSession, post_id: int) -> Post | None:
    stmt = select(Post).where(Post.id == post_id, Post.is_draft == False)  # noqa: E712
    return (await db.execute(stmt)).scalar_one_or_none()


async def update_post(db: AsyncSession, post: Post, request: "UpdatePostRequest") -> Post:
    if request.title is not None:
        post.title = request.title
    if request.description is not None:
        post.description = request.description
    if request.is_free is not None:
        post.is_free = request.is_free
        if request.is_free:
            post.price = None
    if request.price is not None and not post.is_free:
        post.price = request.price
    if request.trade_place is not None:
        post.trade_place = request.trade_place
    if request.photos is not None:
        post.photos = request.photos
    try:
        await db.commit()
        await db.refresh(post)
    except IntegrityError as e:
        await db.rollback()
        raise AppException(
            code="POST_UPDATE_FAILED",
            detail="게시글 수정에 실패했습니다.",
            status_code=422,
        ) from e
    return post


async def delete_post_by_id(db: AsyncSession, post_id: int) -> None:
    await db.execute(delete(Post).where(Post.id == post_id))
    await db.commit()


async def toggle_like(db: AsyncSession, user_email: str, post_id: int) -> tuple[bool, int]:
    stmt = select(Like).where(Like.user_email == user_email, Like.post_id == post_id)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        await db.delete(existing)
        is_liked = False
    else:
        db.add(Like(user_email=user_email, post_id=post_id))
        is_liked = True
    await db.commit()
    count_stmt = select(func.count(Like.id)).where(Like.post_id == post_id)
    like_count = (await db.execute(count_stmt)).scalar_one()
    return is_liked, like_count


async def is_liked_by(db: AsyncSession, user_email: str, post_id: int) -> bool:
    stmt = select(Like).where(Like.user_email == user_email, Like.post_id == post_id)
    return (await db.execute(stmt)).scalar_one_or_none() is not None


async def get_post_detail(
    db: AsyncSession,
    post_id: int,
) -> tuple[Post, int, int, float] | None:
    like_count_sq = (
        select(func.count(Like.id))
        .where(Like.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
    )
    chat_count_sq = (
        select(func.count(ChatMessage.id))
        .where(ChatMessage.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
    )

    stmt = (
        select(
            Post,
            User.manner_temp,
            like_count_sq.label("like_count"),
            chat_count_sq.label("chat_count"),
        )
        .join(User, User.email == Post.seller_email)
        .where(Post.id == post_id, Post.is_draft == False)  # noqa: E712
    )
    row = (await db.execute(stmt)).first()
    if row is None:
        return None
    post, manner_temp, like_count, chat_count = row
    return post, like_count, chat_count, manner_temp


async def increment_view_count(db: AsyncSession, post_id: int) -> None:
    stmt = update(Post).where(Post.id == post_id).values(view_count=Post.view_count + 1)
    await db.execute(stmt)
    await db.commit()


async def get_draft(db: AsyncSession, seller_email: str) -> Post | None:
    stmt = (
        select(Post)
        .where(Post.seller_email == seller_email, Post.is_draft == True)  # noqa: E712
        .limit(1)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def upsert_draft(
    db: AsyncSession,
    *,
    seller_email: str,
    request: "SaveDraftRequest",
) -> Post:
    existing = await get_draft(db, seller_email)
    if existing:
        existing.title = request.title
        existing.description = request.description
        existing.price = request.price
        existing.is_free = request.is_free
        existing.trade_place = request.trade_place
        existing.photos = request.photos
        post = existing
    else:
        post = Post(
            seller_email=seller_email,
            title=request.title,
            description=request.description,
            price=request.price,
            is_free=request.is_free,
            trade_place=request.trade_place,
            photos=request.photos,
            status="판매중",
            is_draft=True,
        )
        db.add(post)
    try:
        await db.commit()
        await db.refresh(post)
    except IntegrityError as e:
        await db.rollback()
        raise AppException(
            code="DRAFT_SAVE_FAILED",
            detail="임시저장에 실패했습니다.",
            status_code=422,
        ) from e
    return post


async def get_post_buyers(db: AsyncSession, post_id: int) -> list[str]:
    stmt = (
        select(distinct(ChatMessage.buyer_email))
        .where(
            ChatMessage.post_id == post_id,
            ChatMessage.buyer_email.is_not(None),
        )
    )
    return list((await db.execute(stmt)).scalars().all())


async def get_my_posts(
    db: AsyncSession, seller_email: str, status: str | None
) -> tuple[list, int]:
    like_count_sq = (
        select(func.count(Like.id))
        .where(Like.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
    )
    chat_count_sq = (
        select(func.count(ChatMessage.id))
        .where(ChatMessage.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
    )

    filters = [Post.seller_email == seller_email, Post.is_draft == False]  # noqa: E712
    if status is not None:
        filters.append(Post.status == status)

    stmt = (
        select(Post, like_count_sq.label("like_count"), chat_count_sq.label("chat_count"))
        .where(*filters)
        .order_by(Post.updated_at.desc())
    )
    rows = (await db.execute(stmt)).all()
    return rows, len(rows)


async def get_my_purchases(db: AsyncSession, buyer_email: str) -> tuple[list, int]:
    stmt = (
        select(Post)
        .where(
            Post.buyer_email == buyer_email,
            Post.status == '거래완료',
            Post.is_draft == False,  # noqa: E712
        )
        .order_by(Post.updated_at.desc())
    )
    rows = list((await db.execute(stmt)).scalars().all())
    return rows, len(rows)


async def get_liked_posts(db: AsyncSession, user_email: str) -> tuple[list, int]:
    like_count_sq = (
        select(func.count(Like.id))
        .where(Like.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
    )
    chat_count_sq = (
        select(func.count(ChatMessage.id))
        .where(ChatMessage.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
    )

    stmt = (
        select(Post, like_count_sq.label("like_count"), chat_count_sq.label("chat_count"))
        .join(Like, Like.post_id == Post.id)
        .where(
            Like.user_email == user_email,
            Post.is_draft == False,  # noqa: E712
        )
        .order_by(Like.created_at.desc())
    )
    rows = (await db.execute(stmt)).all()
    return rows, len(rows)


async def create_post(
    db: AsyncSession,
    *,
    seller_email: str,
    request: "CreatePostRequest",
) -> Post:
    post = Post(
        seller_email=seller_email,
        title=request.title,
        description=request.description,
        price=request.price,
        is_free=request.is_free,
        trade_place=request.trade_place,
        photos=request.photos,
        status="판매중",
        is_draft=False,
    )
    db.add(post)
    try:
        await db.commit()
        await db.refresh(post)
    except IntegrityError as e:
        await db.rollback()
        raise AppException(
            code="POST_CREATE_FAILED",
            detail="게시글 생성에 실패했습니다.",
            status_code=422,
        ) from e
    return post
