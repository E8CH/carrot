import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.features.chats.schemas import ChatRoomListItem, ChatRoomResponse, MessageResponse, UnreadCountResponse
from app.features.chats.service import create_or_get_chat_room, get_chat_messages, get_unread_count, list_chat_rooms, mark_room_as_read, send_message
from app.shared.exceptions import AppException


def make_mock_post(seller_email: str = "seller@example.com"):
    post = MagicMock()
    post.seller_email = seller_email
    return post


@pytest.mark.asyncio
async def test_create_chat_success():
    """정상 채팅방 생성 → ChatRoomResponse 반환"""
    db = AsyncMock()
    post = make_mock_post()

    with (
        patch("app.features.chats.service.posts_repository.get_post_by_id", new=AsyncMock(return_value=post)),
        patch("app.features.chats.service.repository.get_or_create_room", new=AsyncMock(return_value="test-uuid-room")),
    ):
        result = await create_or_get_chat_room(db, "buyer@example.com", 1)

    assert isinstance(result, ChatRoomResponse)
    assert result.room_id == "test-uuid-room"
    assert result.seller_email == "seller@example.com"
    assert result.buyer_email == "buyer@example.com"
    assert result.post_id == 1


@pytest.mark.asyncio
async def test_self_chat_forbidden():
    """본인 게시글 채팅 시도 → SELF_CHAT_FORBIDDEN (403)"""
    db = AsyncMock()
    post = make_mock_post(seller_email="user@example.com")

    with patch("app.features.chats.service.posts_repository.get_post_by_id", new=AsyncMock(return_value=post)):
        with pytest.raises(AppException) as exc_info:
            await create_or_get_chat_room(db, "user@example.com", 1)

    assert exc_info.value.code == "SELF_CHAT_FORBIDDEN"
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_post_not_found():
    """존재하지 않는 게시글 → POST_NOT_FOUND (404)"""
    db = AsyncMock()

    with patch("app.features.chats.service.posts_repository.get_post_by_id", new=AsyncMock(return_value=None)):
        with pytest.raises(AppException) as exc_info:
            await create_or_get_chat_room(db, "buyer@example.com", 999)

    assert exc_info.value.code == "POST_NOT_FOUND"
    assert exc_info.value.status_code == 404


# ─── send_message / get_chat_messages 테스트 ──────────────────────────────────

def make_mock_message(room_id="test-room", seller_email="seller@example.com", buyer_email="buyer@example.com"):
    msg = MagicMock()
    msg.id = 1
    msg.room_id = room_id
    msg.message = "안녕하세요"
    msg.sender_email = buyer_email
    msg.seller_email = seller_email
    msg.buyer_email = buyer_email
    msg.post_id = 1
    msg.sent_at = datetime(2026, 5, 30, 12, 0, 0, tzinfo=timezone.utc)
    msg.is_read = False
    return msg


@pytest.mark.asyncio
async def test_send_message_success_first_message():
    """첫 메시지 전송 — post에서 seller 유추, buyer = sender"""
    db = AsyncMock()
    post = make_mock_post()
    msg = make_mock_message()

    with (
        patch("app.features.chats.service.repository.get_room_context", new=AsyncMock(return_value=None)),
        patch("app.features.chats.service.posts_repository.get_post_by_id", new=AsyncMock(return_value=post)),
        patch("app.features.chats.service.repository.create_message", new=AsyncMock(return_value=msg)),
    ):
        result = await send_message(db, "test-room", "buyer@example.com", 1, "안녕하세요")

    assert isinstance(result, MessageResponse)
    assert result.id == 1


@pytest.mark.asyncio
async def test_send_message_forbidden_non_participant():
    """채팅방 비참여자 메시지 전송 → FORBIDDEN (403)"""
    db = AsyncMock()
    existing = make_mock_message()

    with patch("app.features.chats.service.repository.get_room_context", new=AsyncMock(return_value=existing)):
        with pytest.raises(AppException) as exc_info:
            await send_message(db, "test-room", "stranger@example.com", 1, "해킹 시도")

    assert exc_info.value.code == "FORBIDDEN"
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_get_unread_count_success():
    """미읽음 채팅방 수 반환"""
    db = AsyncMock()
    with patch("app.features.chats.service.repository.get_unread_count", new=AsyncMock(return_value=3)):
        result = await get_unread_count(db, "user@example.com")
    assert isinstance(result, UnreadCountResponse)
    assert result.count == 3


@pytest.mark.asyncio
async def test_mark_room_as_read_success():
    """채팅방 읽음 처리 — 예외 없이 완료"""
    db = AsyncMock()
    with patch("app.features.chats.service.repository.mark_room_as_read", new=AsyncMock(return_value=None)):
        await mark_room_as_read(db, "test-room", "user@example.com")


@pytest.mark.asyncio
async def test_list_chat_rooms_success():
    """채팅 목록 정상 반환 → ChatRoomListItem 리스트"""
    db = AsyncMock()
    msg = make_mock_message()
    photos = ["https://example.com/thumb.jpg"]
    rows = [(msg, photos, 2)]

    with patch("app.features.chats.service.repository.get_chat_rooms", new=AsyncMock(return_value=rows)):
        result = await list_chat_rooms(db, "seller@example.com")

    assert len(result) == 1
    assert isinstance(result[0], ChatRoomListItem)
    assert result[0].opponent_email == "buyer@example.com"
    assert result[0].unread_count == 2
    assert result[0].post_thumbnail == "https://example.com/thumb.jpg"
    assert result[0].seller_email == "seller@example.com"
    assert result[0].buyer_email == "buyer@example.com"


@pytest.mark.asyncio
async def test_list_chat_rooms_empty():
    """채팅방 없을 때 빈 리스트 반환"""
    db = AsyncMock()
    with patch("app.features.chats.service.repository.get_chat_rooms", new=AsyncMock(return_value=[])):
        result = await list_chat_rooms(db, "user@example.com")
    assert result == []


@pytest.mark.asyncio
async def test_get_chat_messages_success():
    """메시지 목록 조회 → MessageResponse 리스트 반환"""
    db = AsyncMock()
    existing = make_mock_message()
    msg = make_mock_message()

    with (
        patch("app.features.chats.service.repository.get_room_context", new=AsyncMock(return_value=existing)),
        patch("app.features.chats.service.repository.get_messages", new=AsyncMock(return_value=[msg])),
    ):
        result = await get_chat_messages(db, "test-room", "buyer@example.com")

    assert len(result) == 1
    assert isinstance(result[0], MessageResponse)
