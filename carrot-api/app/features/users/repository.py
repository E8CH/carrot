from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.users.models import User
from app.shared.exceptions import AppException


async def update_manner_temp(db: AsyncSession, email: str, delta: float) -> None:
    stmt = (
        update(User)
        .where(User.email == email)
        .values(
            manner_temp=func.least(99.0, func.greatest(0.0, User.manner_temp + delta))
        )
    )
    await db.execute(stmt)
    await db.commit()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    *,
    email: str,
    hashed_password: str,
    address: str,
    phone: str,
) -> User:
    user = User(
        email=email,
        hashed_password=hashed_password,
        address=address,
        phone=phone,
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # 동시 요청 race condition: SELECT 통과 후 INSERT 충돌 → 409로 변환
        raise AppException(
            code="EMAIL_ALREADY_EXISTS",
            detail="이미 사용 중인 이메일입니다.",
            status_code=409,
        )
    await db.refresh(user)
    return user
