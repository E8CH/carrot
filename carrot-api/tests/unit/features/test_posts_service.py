import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.features.posts.schemas import CreatePostRequest, DraftResponse, LikeResponse, PostDetailResponse, PostListResponse, SaveDraftRequest, UpdatePostRequest
from app.features.posts.service import change_post_status, complete_post, create_post, delete_post, get_draft, get_post_buyers, get_post_detail, list_posts, save_draft, toggle_like, update_post
from app.shared.exceptions import AppException


_SENTINEL = object()

def make_mock_post(post_id: int, title: str = "테스트 게시글", photos=_SENTINEL):
    post = MagicMock()
    post.id = post_id
    post.title = title
    post.price = 10000
    post.is_free = False
    post.status = "판매중"
    post.photos = ["https://example.com/photo.jpg"] if photos is _SENTINEL else photos
    post.is_draft = False
    post.created_at = datetime(2026, 5, 29, 12, 0, 0, tzinfo=timezone.utc)
    return post


@pytest.mark.asyncio
async def test_list_posts_success():
    """정상 목록 조회: PostListResponse 반환"""
    db = AsyncMock()
    mock_post = make_mock_post(1)
    rows = [(mock_post, 3, 5)]  # (post, like_count, chat_count)

    with patch("app.features.posts.service.repository.get_posts", new=AsyncMock(return_value=(rows, 1))):
        result = await list_posts(db, page=1, size=20)

    assert isinstance(result, PostListResponse)
    assert result.total == 1
    assert result.page == 1
    assert result.size == 20
    assert len(result.items) == 1
    item = result.items[0]
    assert item.id == 1
    assert item.like_count == 3
    assert item.chat_count == 5
    assert item.thumbnail == "https://example.com/photo.jpg"


@pytest.mark.asyncio
async def test_list_posts_empty():
    """빈 목록: items=[], total=0"""
    db = AsyncMock()

    with patch("app.features.posts.service.repository.get_posts", new=AsyncMock(return_value=([], 0))):
        result = await list_posts(db, page=1, size=20)

    assert result.total == 0
    assert result.items == []


@pytest.mark.asyncio
async def test_list_posts_no_photo():
    """사진 없는 게시글: thumbnail=None"""
    db = AsyncMock()
    mock_post = make_mock_post(1, photos=[])
    rows = [(mock_post, 0, 0)]

    with patch("app.features.posts.service.repository.get_posts", new=AsyncMock(return_value=(rows, 1))):
        result = await list_posts(db, page=1, size=20)

    assert result.items[0].thumbnail is None


@pytest.mark.asyncio
async def test_list_posts_pagination():
    """페이지 파라미터 검증: page=2"""
    db = AsyncMock()
    mock_get = AsyncMock(return_value=([], 100))

    with patch("app.features.posts.service.repository.get_posts", new=mock_get):
        result = await list_posts(db, page=2, size=20)

    mock_get.assert_called_once_with(db, 2, 20)
    assert result.page == 2
    assert result.total == 100


# ─── create_post 테스트 ───────────────────────────────────────────────────────

def make_create_request(**overrides):
    defaults = dict(
        title="아이폰 팝니다",
        description="상태 좋습니다",
        price=500000,
        is_free=False,
        photos=["https://example.com/photo.jpg"],
    )
    defaults.update(overrides)
    return CreatePostRequest(**defaults)


def make_mock_created_post():
    post = MagicMock()
    post.id = 1
    post.seller_email = "seller@example.com"
    post.title = "아이폰 팝니다"
    post.description = "상태 좋습니다"
    post.price = 500000
    post.is_free = False
    post.status = "판매중"
    post.trade_place = None
    post.photos = ["https://example.com/photo.jpg"]
    post.view_count = 0
    post.created_at = datetime(2026, 5, 29, tzinfo=timezone.utc)
    post.updated_at = datetime(2026, 5, 29, tzinfo=timezone.utc)
    return post


@pytest.mark.asyncio
async def test_create_post_success():
    """정상 게시글 생성: PostDetailResponse 반환"""
    db = AsyncMock()
    request = make_create_request()
    mock_post = make_mock_created_post()

    with patch("app.features.posts.service.repository.create_post", new=AsyncMock(return_value=mock_post)):
        result = await create_post(db, "seller@example.com", request)

    assert isinstance(result, PostDetailResponse)
    assert result.status == "판매중"
    assert result.id == 1


@pytest.mark.asyncio
async def test_create_post_no_photos():
    """사진 0장: PHOTO_REQUIRED (422)"""
    db = AsyncMock()
    request = make_create_request(photos=[])

    with pytest.raises(AppException) as exc_info:
        await create_post(db, "seller@example.com", request)

    assert exc_info.value.code == "PHOTO_REQUIRED"
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_create_post_is_free_no_price():
    """is_free=True, price=None: 정상 생성"""
    db = AsyncMock()
    request = make_create_request(is_free=True, price=None)
    mock_post = make_mock_created_post()
    mock_post.is_free = True
    mock_post.price = None

    with patch("app.features.posts.service.repository.create_post", new=AsyncMock(return_value=mock_post)):
        result = await create_post(db, "seller@example.com", request)

    assert result.is_free is True
    assert result.price is None


# ─── draft 테스트 ─────────────────────────────────────────────────────────────

def make_mock_draft(title: str = "임시 제목"):
    post = MagicMock()
    post.id = 99
    post.title = title
    post.description = "임시 설명"
    post.price = None
    post.is_free = False
    post.trade_place = None
    post.photos = []
    post.updated_at = datetime(2026, 5, 30, tzinfo=timezone.utc)
    return post


def make_draft_request(**overrides):
    defaults = dict(title="임시 제목", description="임시 설명")
    defaults.update(overrides)
    return SaveDraftRequest(**defaults)


@pytest.mark.asyncio
async def test_get_draft_returns_response():
    """임시저장 존재 시 DraftResponse 반환"""
    db = AsyncMock()
    mock_draft = make_mock_draft()

    with patch("app.features.posts.service.repository.get_draft", new=AsyncMock(return_value=mock_draft)):
        result = await get_draft(db, "seller@example.com")

    assert isinstance(result, DraftResponse)
    assert result.id == 99
    assert result.title == "임시 제목"


@pytest.mark.asyncio
async def test_get_draft_returns_none():
    """임시저장 없을 때 None 반환"""
    db = AsyncMock()

    with patch("app.features.posts.service.repository.get_draft", new=AsyncMock(return_value=None)):
        result = await get_draft(db, "seller@example.com")

    assert result is None


@pytest.mark.asyncio
async def test_save_draft_success():
    """정상 저장 → DraftResponse 반환"""
    db = AsyncMock()
    request = make_draft_request()
    mock_draft = make_mock_draft()

    with patch("app.features.posts.service.repository.upsert_draft", new=AsyncMock(return_value=mock_draft)):
        result = await save_draft(db, "seller@example.com", request)

    assert isinstance(result, DraftResponse)
    assert result.id == 99


@pytest.mark.asyncio
async def test_save_draft_empty_fields():
    """빈 제목/설명/사진도 저장 성공 (publish와 달리 검증 없음)"""
    db = AsyncMock()
    request = make_draft_request(title="", description="", photos=[])
    mock_draft = make_mock_draft(title="")
    mock_draft.description = ""

    with patch("app.features.posts.service.repository.upsert_draft", new=AsyncMock(return_value=mock_draft)):
        result = await save_draft(db, "seller@example.com", request)

    assert isinstance(result, DraftResponse)
    assert result.photos == []


# ─── get_post_detail 테스트 ───────────────────────────────────────────────────

def make_mock_post_full(post_id: int = 1):
    post = MagicMock()
    post.id = post_id
    post.seller_email = "seller@example.com"
    post.title = "아이폰 팝니다"
    post.description = "상태 좋습니다"
    post.price = 500000
    post.is_free = False
    post.status = "판매중"
    post.trade_place = None
    post.photos = ["https://example.com/photo.jpg"]
    post.view_count = 5
    post.is_draft = False
    post.created_at = datetime(2026, 5, 30, tzinfo=timezone.utc)
    post.updated_at = datetime(2026, 5, 30, tzinfo=timezone.utc)
    return post


@pytest.mark.asyncio
async def test_get_post_detail_success():
    """정상 조회: PostDetailResponse (chat_count, like_count, manner_temp 포함)"""
    db = AsyncMock()
    mock_post = make_mock_post_full()
    detail_result = (mock_post, 3, 7, 42.5)  # (post, like_count, chat_count, manner_temp)

    with (
        patch("app.features.posts.service.repository.get_post_detail", new=AsyncMock(return_value=detail_result)),
        patch("app.features.posts.service.repository.increment_view_count", new=AsyncMock()),
    ):
        result = await get_post_detail(db, 1)

    assert isinstance(result, PostDetailResponse)
    assert result.id == 1
    assert result.like_count == 3
    assert result.chat_count == 7
    assert result.manner_temp == 42.5
    assert result.view_count == 6  # view_count + 1


@pytest.mark.asyncio
async def test_get_post_detail_not_found():
    """존재하지 않는 게시글: POST_NOT_FOUND (404)"""
    db = AsyncMock()

    with patch("app.features.posts.service.repository.get_post_detail", new=AsyncMock(return_value=None)):
        with pytest.raises(AppException) as exc_info:
            await get_post_detail(db, 999)

    assert exc_info.value.code == "POST_NOT_FOUND"
    assert exc_info.value.status_code == 404


# ─── update_post / delete_post 테스트 ─────────────────────────────────────────

def make_update_request(**overrides):
    defaults = dict(title="수정된 제목")
    defaults.update(overrides)
    return UpdatePostRequest(**defaults)


@pytest.mark.asyncio
async def test_update_post_success():
    """본인 게시글 수정 → PostDetailResponse 반환"""
    db = AsyncMock()
    post = make_mock_post_full()
    updated = make_mock_post_full()
    updated.title = "수정된 제목"
    request = make_update_request()

    with (
        patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)),
        patch("app.features.posts.service.repository.update_post", new=AsyncMock(return_value=updated)),
    ):
        result = await update_post(db, "seller@example.com", 1, request)

    assert isinstance(result, PostDetailResponse)
    assert result.title == "수정된 제목"


@pytest.mark.asyncio
async def test_update_post_forbidden():
    """타인 게시글 수정 → FORBIDDEN (403)"""
    db = AsyncMock()
    post = make_mock_post_full()  # seller_email = "seller@example.com"

    with patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)):
        with pytest.raises(AppException) as exc_info:
            await update_post(db, "other@example.com", 1, make_update_request())

    assert exc_info.value.code == "FORBIDDEN"
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_delete_post_success():
    """본인 게시글 소유권 검증 + photos 반환 (DB 삭제는 delete_post_db가 담당)"""
    db = AsyncMock()
    post = make_mock_post_full()
    post.photos = ["https://example.com/photo.jpg"]

    with patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)):
        photos = await delete_post(db, "seller@example.com", 1)

    assert photos == ["https://example.com/photo.jpg"]


@pytest.mark.asyncio
async def test_delete_post_forbidden():
    """타인 게시글 삭제 → FORBIDDEN (403)"""
    db = AsyncMock()
    post = make_mock_post_full()

    with patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)):
        with pytest.raises(AppException) as exc_info:
            await delete_post(db, "other@example.com", 1)

    assert exc_info.value.code == "FORBIDDEN"
    assert exc_info.value.status_code == 403


# ─── change_post_status 테스트 ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_change_post_status_success():
    """판매자 본인 게시글 상태 변경 (판매중 → 예약중) → PostDetailResponse 반환"""
    db = AsyncMock()
    post = make_mock_post_full()
    post.status = "판매중"

    with (
        patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)),
        patch.object(db, "commit", new=AsyncMock()),
        patch.object(db, "refresh", new=AsyncMock()),
    ):
        result = await change_post_status(db, "seller@example.com", 1, "예약중")

    assert isinstance(result, PostDetailResponse)
    assert result.status == "예약중"
    assert post.status == "예약중"


@pytest.mark.asyncio
async def test_change_post_status_locked():
    """거래완료 게시글 상태 변경 시도 → STATUS_LOCKED (422)"""
    db = AsyncMock()
    post = make_mock_post_full()
    post.status = "거래완료"

    with patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)):
        with pytest.raises(AppException) as exc_info:
            await change_post_status(db, "seller@example.com", 1, "판매중")

    assert exc_info.value.code == "TRADE_ALREADY_COMPLETED"
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_change_post_status_forbidden():
    """타인 게시글 상태 변경 시도 → FORBIDDEN (403)"""
    db = AsyncMock()
    post = make_mock_post_full()  # seller_email = "seller@example.com"

    with patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)):
        with pytest.raises(AppException) as exc_info:
            await change_post_status(db, "other@example.com", 1, "예약중")

    assert exc_info.value.code == "FORBIDDEN"
    assert exc_info.value.status_code == 403


# ─── toggle_like 테스트 ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_toggle_like_success():
    """찜 토글 → LikeResponse(is_liked, like_count) 반환"""
    db = AsyncMock()
    post = make_mock_post_full()

    with (
        patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)),
        patch("app.features.posts.service.repository.toggle_like", new=AsyncMock(return_value=(True, 5))),
    ):
        result = await toggle_like(db, "buyer@example.com", 1)

    assert isinstance(result, LikeResponse)
    assert result.is_liked is True
    assert result.like_count == 5


@pytest.mark.asyncio
async def test_toggle_like_unlike():
    """이미 찜한 게시글 재호출 → is_liked=False (해제)"""
    db = AsyncMock()
    post = make_mock_post_full()

    with (
        patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)),
        patch("app.features.posts.service.repository.toggle_like", new=AsyncMock(return_value=(False, 4))),
    ):
        result = await toggle_like(db, "buyer@example.com", 1)

    assert result.is_liked is False
    assert result.like_count == 4


@pytest.mark.asyncio
async def test_toggle_like_post_not_found():
    """존재하지 않는 게시글 찜 → POST_NOT_FOUND (404)"""
    db = AsyncMock()

    with patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=None)):
        with pytest.raises(AppException) as exc_info:
            await toggle_like(db, "buyer@example.com", 999)

    assert exc_info.value.code == "POST_NOT_FOUND"
    assert exc_info.value.status_code == 404


# ─── get_post_buyers 테스트 ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_post_buyers_success():
    """정상 구매자 목록 조회: BuyersResponse 반환"""
    from app.features.posts.schemas import BuyersResponse
    db = AsyncMock()
    post = make_mock_post_full()

    with (
        patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)),
        patch("app.features.posts.service.repository.get_post_buyers", new=AsyncMock(return_value=["buyer@example.com", "buyer2@example.com"])),
    ):
        result = await get_post_buyers(db, "seller@example.com", 1)

    assert isinstance(result, BuyersResponse)
    assert len(result.buyers) == 2
    assert result.buyers[0].buyer_email == "buyer@example.com"


@pytest.mark.asyncio
async def test_get_post_buyers_forbidden():
    """타인이 구매자 목록 조회 시도 → FORBIDDEN (403)"""
    db = AsyncMock()
    post = make_mock_post_full()  # seller_email = "seller@example.com"

    with patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)):
        with pytest.raises(AppException) as exc_info:
            await get_post_buyers(db, "other@example.com", 1)

    assert exc_info.value.code == "FORBIDDEN"
    assert exc_info.value.status_code == 403


# ─── complete_post 테스트 ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_complete_post_success():
    """정상 거래완료: status='거래완료', buyer_email 저장"""
    db = AsyncMock()
    post = make_mock_post_full()
    post.status = "예약중"
    post.buyer_email = None

    with (
        patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)),
        patch("app.features.posts.service.repository.get_post_buyers", new=AsyncMock(return_value=["buyer@example.com"])),
        patch.object(db, "commit", new=AsyncMock()),
        patch.object(db, "refresh", new=AsyncMock()),
    ):
        result = await complete_post(db, "seller@example.com", 1, "buyer@example.com")

    assert isinstance(result, PostDetailResponse)
    assert result.status == "거래완료"
    assert post.status == "거래완료"
    assert post.buyer_email == "buyer@example.com"


@pytest.mark.asyncio
async def test_complete_post_self_trade():
    """판매자 본인을 구매자로 지정 → SELF_TRADE_FORBIDDEN (422)"""
    db = AsyncMock()
    post = make_mock_post_full()
    post.status = "예약중"

    with patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)):
        with pytest.raises(AppException) as exc_info:
            await complete_post(db, "seller@example.com", 1, "seller@example.com")

    assert exc_info.value.code == "SELF_TRADE_FORBIDDEN"
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_complete_post_invalid_buyer():
    """채팅하지 않은 사람을 구매자로 지정 → INVALID_BUYER (422)"""
    db = AsyncMock()
    post = make_mock_post_full()
    post.status = "예약중"

    with (
        patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)),
        patch("app.features.posts.service.repository.get_post_buyers", new=AsyncMock(return_value=["buyer@example.com"])),
    ):
        with pytest.raises(AppException) as exc_info:
            await complete_post(db, "seller@example.com", 1, "stranger@example.com")

    assert exc_info.value.code == "INVALID_BUYER"
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_complete_post_already_completed():
    """이미 거래완료된 게시글 → TRADE_ALREADY_COMPLETED (422)"""
    db = AsyncMock()
    post = make_mock_post_full()
    post.status = "거래완료"

    with patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)):
        with pytest.raises(AppException) as exc_info:
            await complete_post(db, "seller@example.com", 1, "buyer@example.com")

    assert exc_info.value.code == "TRADE_ALREADY_COMPLETED"
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_complete_post_forbidden():
    """타인 거래완료 시도 → FORBIDDEN (403)"""
    db = AsyncMock()
    post = make_mock_post_full()  # seller_email = "seller@example.com"

    with patch("app.features.posts.service.repository.get_post_by_id", new=AsyncMock(return_value=post)):
        with pytest.raises(AppException) as exc_info:
            await complete_post(db, "other@example.com", 1, "buyer@example.com")

    assert exc_info.value.code == "FORBIDDEN"
    assert exc_info.value.status_code == 403
