from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False, default="user")  # 'user' | 'admin'
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    manner_temp: Mapped[float] = mapped_column(Float, nullable=False, default=36.5)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
