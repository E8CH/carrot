from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # room_id는 서비스 레이어에서 명시적으로 주입해야 함 (default 없음)
    # 같은 채팅방의 메시지는 동일한 room_id를 공유
    room_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), nullable=False, index=True
    )
    seller_email: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=False
    )
    buyer_email: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=False
    )
    post_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sender_email: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=False
    )
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
