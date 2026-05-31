from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class AdminRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class AdminUserItem(BaseModel):
    email: str
    created_at: datetime
    manner_temp: float
    post_count: int
    is_active: bool


class AdminUsersResponse(BaseModel):
    items: list[AdminUserItem]
    total: int


class AdminUserStatusRequest(BaseModel):
    is_active: bool


class AdminPostItem(BaseModel):
    id: int
    title: str
    seller_email: str
    price: int | None
    is_free: bool
    status: str
    created_at: datetime


class AdminPostsResponse(BaseModel):
    items: list[AdminPostItem]
    total: int


class AdminChatRoomItem(BaseModel):
    room_id: str
    seller_email: str
    buyer_email: str
    post_title: str
    message_count: int
    last_message_at: datetime


class AdminChatRoomsResponse(BaseModel):
    items: list[AdminChatRoomItem]
    total: int


class AdminChatMessageItem(BaseModel):
    id: int
    sender_email: str
    message: str
    sent_at: datetime


class AdminChatMessagesResponse(BaseModel):
    room_id: str
    items: list[AdminChatMessageItem]
