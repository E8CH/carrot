from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    seller_email: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_free: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="판매중")  # 판매중|예약중|거래완료
    trade_place: Mapped[str | None] = mapped_column(String(200), nullable=True)
    photos: Mapped[list] = mapped_column(ARRAY(Text), nullable=False, default=list)
    buyer_email: Mapped[str | None] = mapped_column(
        String(255), ForeignKey("users.email", ondelete="SET NULL"), nullable=True
    )
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_draft: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_email: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=False
    )
    post_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    from sqlalchemy import UniqueConstraint
    __table_args__ = (UniqueConstraint("user_email", "post_id", name="uq_likes_user_post"),)
