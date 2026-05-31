from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.posts import repository
from app.features.posts.schemas import (
    BuyerItem,
    BuyersResponse,
    CompletePostRequest,
    CreatePostRequest,
    DraftResponse,
    LikeResponse,
    MyPostsResponse,
    PostDetailResponse,
    PostListItem,
    PostListResponse,
    PostStatusRequest,
    PurchaseItem,
    PurchasesResponse,
    SaveDraftRequest,
    UpdatePostRequest,
)
from app.features.posts.models import Post
from app.shared.exceptions import AppException


async def list_posts(db: AsyncSession, page: int, size: int) -> PostListResponse:
    rows, total = await repository.get_posts(db, page, size)

    items: list[PostListItem] = []
    for post, like_count, chat_count in rows:
        thumbnail = post.photos[0] if post.photos else None
        items.append(
            PostListItem(
                id=post.id,
                title=post.title,
                price=post.price,
                is_free=post.is_free,
                status=post.status,
                thumbnail=thumbnail,
                chat_count=chat_count,
                like_count=like_count,
                created_at=post.created_at,
            )
        )

    return PostListResponse(items=items, total=total, page=page, size=size)


async def get_my_posts(
    db: AsyncSession,
    seller_email: str,
    status: str | None,
) -> MyPostsResponse:
    rows, total = await repository.get_my_posts(db, seller_email, status)
    items: list[PostListItem] = []
    for post, like_count, chat_count in rows:
        thumbnail = post.photos[0] if post.photos else None
        items.append(
            PostListItem(
                id=post.id,
                title=post.title,
                price=post.price,
                is_free=post.is_free,
                status=post.status,
                thumbnail=thumbnail,
                chat_count=chat_count,
                like_count=like_count,
                created_at=post.created_at,
            )
        )
    return MyPostsResponse(items=items, total=total)


async def get_liked_posts(db: AsyncSession, user_email: str) -> MyPostsResponse:
    rows, total = await repository.get_liked_posts(db, user_email)
    items: list[PostListItem] = []
    for post, like_count, chat_count in rows:
        thumbnail = post.photos[0] if post.photos else None
        items.append(
            PostListItem(
                id=post.id,
                title=post.title,
                price=post.price,
                is_free=post.is_free,
                status=post.status,
                thumbnail=thumbnail,
                chat_count=chat_count,
                like_count=like_count,
                created_at=post.created_at,
            )
        )
    return MyPostsResponse(items=items, total=total)


async def get_my_purchases(db: AsyncSession, buyer_email: str) -> PurchasesResponse:
    posts, total = await repository.get_my_purchases(db, buyer_email)
    items = [
        PurchaseItem(
            id=post.id,
            title=post.title,
            thumbnail=post.photos[0] if post.photos else None,
            price=post.price,
            is_free=post.is_free,
            updated_at=post.updated_at,
        )
        for post in posts
    ]
    return PurchasesResponse(items=items, total=total)


async def _get_owned_post(db: AsyncSession, post_id: int, seller_email: str) -> Post:
    post = await repository.get_post_by_id(db, post_id)
    if post is None:
        raise AppException(code="POST_NOT_FOUND", detail="게시글을 찾을 수 없습니다.", status_code=404)
    if post.seller_email != seller_email:
        raise AppException(code="FORBIDDEN", detail="권한이 없습니다.", status_code=403)
    return post


async def update_post(
    db: AsyncSession,
    seller_email: str,
    post_id: int,
    request: UpdatePostRequest,
) -> PostDetailResponse:
    post = await _get_owned_post(db, post_id, seller_email)
    effective_is_free = request.is_free if request.is_free is not None else post.is_free
    if request.price is not None and effective_is_free:
        raise AppException(
            code="PRICE_NOT_ALLOWED",
            detail="나눔 게시글에는 가격을 설정할 수 없습니다.",
            status_code=422,
        )
    if request.photos is not None and len(request.photos) == 0:
        raise AppException(
            code="PHOTO_REQUIRED",
            detail="사진을 1장 이상 업로드해야 합니다.",
            status_code=422,
        )
    updated = await repository.update_post(db, post, request)
    return PostDetailResponse(
        id=updated.id,
        seller_email=updated.seller_email,
        title=updated.title,
        description=updated.description,
        price=updated.price,
        is_free=updated.is_free,
        status=updated.status,
        trade_place=updated.trade_place,
        photos=updated.photos,
        view_count=updated.view_count,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
        chat_count=0,
        like_count=0,
        manner_temp=36.5,
    )


async def change_post_status(
    db: AsyncSession,
    seller_email: str,
    post_id: int,
    new_status: str,
) -> PostDetailResponse:
    post = await _get_owned_post(db, post_id, seller_email)
    if post.status == '거래완료':
        raise AppException(code="TRADE_ALREADY_COMPLETED", detail="거래완료된 게시글은 상태를 변경할 수 없습니다.", status_code=422)
    post.status = new_status
    try:
        await db.commit()
        await db.refresh(post)
    except IntegrityError as e:
        await db.rollback()
        raise AppException(code="STATUS_CHANGE_FAILED", detail="상태 변경에 실패했습니다.", status_code=422) from e
    return PostDetailResponse(
        id=post.id,
        seller_email=post.seller_email,
        title=post.title,
        description=post.description,
        price=post.price,
        is_free=post.is_free,
        status=post.status,
        trade_place=post.trade_place,
        photos=post.photos,
        view_count=post.view_count,
        created_at=post.created_at,
        updated_at=post.updated_at,
        chat_count=0,
        like_count=0,
        manner_temp=36.5,
        is_liked=False,
    )


async def get_post_buyers(
    db: AsyncSession,
    seller_email: str,
    post_id: int,
) -> BuyersResponse:
    await _get_owned_post(db, post_id, seller_email)
    buyers = await repository.get_post_buyers(db, post_id)
    return BuyersResponse(buyers=[BuyerItem(buyer_email=e) for e in buyers])


async def complete_post(
    db: AsyncSession,
    seller_email: str,
    post_id: int,
    buyer_email: str,
) -> PostDetailResponse:
    post = await _get_owned_post(db, post_id, seller_email)
    if post.status == '거래완료':
        raise AppException(
            code="TRADE_ALREADY_COMPLETED",
            detail="거래완료된 게시글은 상태를 변경할 수 없습니다.",
            status_code=422,
        )
    if buyer_email == seller_email:
        raise AppException(code="SELF_TRADE_FORBIDDEN", detail="본인을 구매자로 지정할 수 없습니다.", status_code=422)
    valid_buyers = await repository.get_post_buyers(db, post_id)
    if buyer_email not in valid_buyers:
        raise AppException(code="INVALID_BUYER", detail="해당 게시글의 구매자가 아닙니다.", status_code=422)
    post.status = '거래완료'
    post.buyer_email = buyer_email
    try:
        await db.commit()
        await db.refresh(post)
    except IntegrityError as e:
        await db.rollback()
        raise AppException(
            code="COMPLETE_FAILED",
            detail="거래완료 처리에 실패했습니다.",
            status_code=422,
        ) from e
    return PostDetailResponse(
        id=post.id,
        seller_email=post.seller_email,
        title=post.title,
        description=post.description,
        price=post.price,
        is_free=post.is_free,
        status=post.status,
        trade_place=post.trade_place,
        photos=post.photos,
        view_count=post.view_count,
        created_at=post.created_at,
        updated_at=post.updated_at,
        chat_count=0,
        like_count=0,
        manner_temp=36.5,
        is_liked=False,
    )


async def delete_post(db: AsyncSession, seller_email: str, post_id: int) -> list[str]:
    """소유권 검증 후 photos 반환. DB 삭제는 하지 않음 (router가 Storage 삭제 후 delete_post_db 호출)."""
    post = await _get_owned_post(db, post_id, seller_email)
    return list(post.photos or [])


async def delete_post_db(db: AsyncSession, post_id: int) -> None:
    await repository.delete_post_by_id(db, post_id)


async def get_post_detail(
    db: AsyncSession,
    post_id: int,
    user_email: str | None = None,
) -> PostDetailResponse:
    result = await repository.get_post_detail(db, post_id)
    if result is None:
        raise AppException(
            code="POST_NOT_FOUND",
            detail="게시글을 찾을 수 없습니다.",
            status_code=404,
        )
    post, like_count, chat_count, manner_temp = result
    await repository.increment_view_count(db, post_id)
    await db.refresh(post)
    is_liked = False
    if user_email:
        is_liked = await repository.is_liked_by(db, user_email, post_id)
    return PostDetailResponse(
        id=post.id,
        seller_email=post.seller_email,
        title=post.title,
        description=post.description,
        price=post.price,
        is_free=post.is_free,
        status=post.status,
        trade_place=post.trade_place,
        photos=post.photos,
        view_count=post.view_count + 1,
        created_at=post.created_at,
        updated_at=post.updated_at,
        chat_count=chat_count,
        like_count=like_count,
        manner_temp=manner_temp,
        is_liked=is_liked,
    )


async def toggle_like(db: AsyncSession, user_email: str, post_id: int) -> LikeResponse:
    post = await repository.get_post_by_id(db, post_id)
    if post is None:
        raise AppException(code="POST_NOT_FOUND", detail="게시글을 찾을 수 없습니다.", status_code=404)
    is_liked, like_count = await repository.toggle_like(db, user_email, post_id)
    return LikeResponse(is_liked=is_liked, like_count=like_count)


async def get_draft(db: AsyncSession, seller_email: str) -> DraftResponse | None:
    post = await repository.get_draft(db, seller_email)
    if post is None:
        return None
    return DraftResponse.model_validate(post)


async def save_draft(
    db: AsyncSession,
    seller_email: str,
    request: SaveDraftRequest,
) -> DraftResponse:
    post = await repository.upsert_draft(db, seller_email=seller_email, request=request)
    return DraftResponse.model_validate(post)


async def create_post(
    db: AsyncSession,
    seller_email: str,
    request: CreatePostRequest,
) -> PostDetailResponse:
    if not request.photos:
        raise AppException(
            code="PHOTO_REQUIRED",
            detail="사진을 1장 이상 업로드해야 합니다.",
            status_code=422,
        )
    post = await repository.create_post(db, seller_email=seller_email, request=request)
    return PostDetailResponse(
        id=post.id,
        seller_email=post.seller_email,
        title=post.title,
        description=post.description,
        price=post.price,
        is_free=post.is_free,
        status=post.status,
        trade_place=post.trade_place,
        photos=post.photos,
        view_count=post.view_count,
        created_at=post.created_at,
        updated_at=post.updated_at,
        chat_count=0,
        like_count=0,
        manner_temp=36.5,
    )
