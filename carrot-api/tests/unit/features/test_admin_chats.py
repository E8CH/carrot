import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.features.admin.schemas import AdminChatRoomsResponse, AdminChatMessagesResponse


def make_admin_dep():
    return {"sub": "admin@example.com", "role": "admin"}


def make_room_row(room_id: str = "room-uuid-1"):
    row = MagicMock()
    row.room_id = room_id
    row.seller_email = "seller@example.com"
    row.buyer_email = "buyer@example.com"
    row.post_title = "테스트 게시글"
    row.message_count = 5
    row.last_message_at = datetime(2026, 5, 30, tzinfo=timezone.utc)
    return row


def make_message(msg_id: int = 1):
    msg = MagicMock()
    msg.id = msg_id
    msg.sender_email = "buyer@example.com"
    msg.message = f"테스트 메시지 {msg_id}"
    msg.sent_at = datetime(2026, 5, 30, tzinfo=timezone.utc)
    return msg


@pytest.mark.asyncio
async def test_get_admin_chats_success():
    """관리자 전체 채팅방 목록 조회 성공"""
    from app.features.admin.router import get_admin_chats
    db = AsyncMock()
    rows = [make_room_row("room-1"), make_room_row("room-2")]

    with patch(
        "app.features.admin.router.admin_repo.get_all_chat_rooms",
        new=AsyncMock(return_value=(rows, 2)),
    ):
        result = await get_admin_chats(make_admin_dep(), db)

    assert isinstance(result, AdminChatRoomsResponse)
    assert result.total == 2
    assert result.items[0].room_id == "room-1"
    assert result.items[0].message_count == 5
    assert result.items[0].post_title == "테스트 게시글"


@pytest.mark.asyncio
async def test_get_admin_chats_empty():
    """채팅방 없는 경우 빈 목록 반환"""
    from app.features.admin.router import get_admin_chats
    db = AsyncMock()

    with patch(
        "app.features.admin.router.admin_repo.get_all_chat_rooms",
        new=AsyncMock(return_value=([], 0)),
    ):
        result = await get_admin_chats(make_admin_dep(), db)

    assert result.total == 0
    assert result.items == []


@pytest.mark.asyncio
async def test_get_admin_chat_messages_success():
    """특정 채팅방 메시지 내역 조회 성공"""
    from app.features.admin.router import get_admin_chat_messages
    db = AsyncMock()
    messages = [make_message(1), make_message(2)]

    with patch(
        "app.features.admin.router.admin_repo.get_room_messages_admin",
        new=AsyncMock(return_value=messages),
    ):
        result = await get_admin_chat_messages("room-uuid-1", make_admin_dep(), db)

    assert isinstance(result, AdminChatMessagesResponse)
    assert result.room_id == "room-uuid-1"
    assert len(result.items) == 2
    assert result.items[0].sender_email == "buyer@example.com"
    assert result.items[0].message == "테스트 메시지 1"


@pytest.mark.asyncio
async def test_get_admin_chat_messages_empty_room():
    """메시지 없는 채팅방 — 빈 목록 반환 (404 아님)"""
    from app.features.admin.router import get_admin_chat_messages
    db = AsyncMock()

    with patch(
        "app.features.admin.router.admin_repo.get_room_messages_admin",
        new=AsyncMock(return_value=[]),
    ):
        result = await get_admin_chat_messages("unknown-room", make_admin_dep(), db)

    assert result.room_id == "unknown-room"
    assert result.items == []
