from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateChatRequest(BaseModel):
    post_id: int = Field(ge=1)


class ChatRoomResponse(BaseModel):
    room_id: str
    post_id: int
    seller_email: str
    buyer_email: str


class UnreadCountResponse(BaseModel):
    count: int


class ChatRoomListItem(BaseModel):
    room_id: str
    post_id: int
    post_thumbnail: str | None
    opponent_email: str
    seller_email: str
    buyer_email: str
    last_message: str
    last_sent_at: datetime
    unread_count: int


class SendMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    post_id: int = Field(ge=1)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: str
    message: str
    sender_email: str
    sent_at: datetime
    is_read: bool
