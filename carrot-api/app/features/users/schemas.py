from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class RegisterRequest(BaseModel):
    email: EmailStr
    # bcrypt는 72바이트에서 잘림. max_length=72로 DoS 방지 + 일관성 보장
    password: str = Field(min_length=8, max_length=72)
    address: str = Field(min_length=1, max_length=500)   # DB 컬럼 상한과 일치
    phone: str = Field(min_length=1, max_length=20)      # DB 컬럼 상한과 일치


class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    address: str
    phone: str
    role: str
    manner_temp: float
    created_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
