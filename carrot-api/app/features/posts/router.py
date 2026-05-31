import uuid

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import create_client

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_user
from app.features.posts import service
from app.features.posts.schemas import (
    BuyersResponse,
    CompletePostRequest,
    CreatePostRequest,
    DraftResponse,
    LikeResponse,
    PostDetailResponse,
    PostListResponse,
    PostStatusRequest,
    SaveDraftRequest,
    UpdatePostRequest,
    UploadUrlResponse,
)
from app.shared.exceptions import AppException

router = APIRouter()

# Supabase 클라이언트 (모듈 로드 시 1회 생성)
_supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
_BUCKET = "posts"


@router.get("/", response_model=PostListResponse)
async def list_posts(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PostListResponse:
    return await service.list_posts(db, page, size)


@router.post("/upload-url", response_model=UploadUrlResponse)
async def get_upload_url(
    current_user: dict = Depends(get_current_user),
) -> UploadUrlResponse:
    seller_email = current_user.get("sub", "unknown")
    file_path = f"{seller_email}/{uuid.uuid4()}.jpg"
    try:
        response = _supabase.storage.from_(_BUCKET).create_signed_upload_url(file_path)
        upload_url = (
            response.get("signedURL")
            or response.get("signed_url")
            or (response.get("data") or {}).get("signed_url")
            or ""
        )
    except Exception as e:
        raise AppException(
            code="UPLOAD_URL_FAILED",
            detail="업로드 URL 생성에 실패했습니다.",
            status_code=500,
        ) from e
    if not upload_url:
        raise AppException(
            code="UPLOAD_URL_FAILED",
            detail="업로드 URL 생성에 실패했습니다.",
            status_code=500,
        )
    return UploadUrlResponse(upload_url=upload_url, file_path=file_path)


# ⚠️ /draft는 /{post_id} 보다 반드시 먼저 등록할 것 (literal path가 path parameter보다 우선)
@router.get("/draft", response_model=DraftResponse)
async def get_draft(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DraftResponse:
    seller_email = current_user.get("sub")
    if not seller_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    draft = await service.get_draft(db, seller_email)
    if draft is None:
        raise AppException(code="DRAFT_NOT_FOUND", detail="임시저장 게시글이 없습니다.", status_code=404)
    return draft


@router.post("/draft", response_model=DraftResponse, status_code=200)
async def save_draft(
    request: SaveDraftRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DraftResponse:
    seller_email = current_user.get("sub")
    if not seller_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return await service.save_draft(db, seller_email, request)


@router.get("/{post_id}", response_model=PostDetailResponse)
async def get_post(
    post_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: dict | None = Depends(get_optional_user),
) -> PostDetailResponse:
    user_email = current_user.get("sub") if current_user else None
    return await service.get_post_detail(db, post_id, user_email)


@router.post("/{post_id}/like", response_model=LikeResponse)
async def toggle_like(
    post_id: int = Path(ge=1),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LikeResponse:
    user_email = current_user.get("sub")
    if not user_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return await service.toggle_like(db, user_email, post_id)


@router.patch("/{post_id}/status", response_model=PostDetailResponse)
async def change_post_status(
    request: PostStatusRequest,
    post_id: int = Path(ge=1),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PostDetailResponse:
    seller_email = current_user.get("sub")
    if not seller_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return await service.change_post_status(db, seller_email, post_id, request.status)


@router.get("/{post_id}/buyers", response_model=BuyersResponse)
async def get_post_buyers(
    post_id: int = Path(ge=1),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BuyersResponse:
    seller_email = current_user.get("sub")
    if not seller_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return await service.get_post_buyers(db, seller_email, post_id)


@router.patch("/{post_id}/complete", response_model=PostDetailResponse)
async def complete_post(
    request: CompletePostRequest,
    post_id: int = Path(ge=1),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PostDetailResponse:
    seller_email = current_user.get("sub")
    if not seller_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return await service.complete_post(db, seller_email, post_id, request.buyer_email)


@router.patch("/{post_id}", response_model=PostDetailResponse)
async def patch_post(
    request: UpdatePostRequest,
    post_id: int = Path(ge=1),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PostDetailResponse:
    seller_email = current_user.get("sub")
    if not seller_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return await service.update_post(db, seller_email, post_id, request)


@router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: int = Path(ge=1),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    seller_email = current_user.get("sub")
    if not seller_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    # 1. 소유권 검증 + photos 조회 (DB 삭제 없음)
    photos = await service.delete_post(db, seller_email, post_id)
    # 2. Storage 먼저 삭제 (AC3: Storage before DB)
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
                pass  # orphan files 허용 (포트폴리오)
    # 3. DB 삭제
    await service.delete_post_db(db, post_id)


@router.post("/", response_model=PostDetailResponse, status_code=201)
async def create_post(
    request: CreatePostRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PostDetailResponse:
    seller_email = current_user.get("sub")
    if not seller_email:
        raise AppException(code="UNAUTHORIZED", detail="유효하지 않은 토큰입니다.", status_code=401)
    return await service.create_post(db, seller_email, request)
