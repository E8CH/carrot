from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    writer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    target_email: Mapped[str] = mapped_column(String(255), nullable=False)
    is_positive: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tags: Mapped[list] = mapped_column(ARRAY(Text), nullable=False, default=list)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("post_id", "writer_email", name="uq_reviews_post_writer"),
    )
