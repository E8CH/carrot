from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class PostListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    price: int | None
    is_free: bool
    status: str
    thumbnail: str | None  # photos[0] 또는 None
    chat_count: int
    like_count: int
    created_at: datetime


class PostListResponse(BaseModel):
    items: list[PostListItem]
    total: int
    page: int
    size: int


class UploadUrlResponse(BaseModel):
    upload_url: str
    file_path: str


class CreatePostRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=2000)
    price: int | None = Field(default=None, ge=0)
    is_free: bool = False
    trade_place: str | None = None
    photos: list[str] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def price_none_when_free(self) -> "CreatePostRequest":
        if self.is_free and self.price is not None:
            raise ValueError("나눔 게시글은 price를 설정할 수 없습니다.")
        return self


class PostDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seller_email: str
    title: str
    description: str
    price: int | None
    is_free: bool
    status: str
    trade_place: str | None
    photos: list[str]
    view_count: int
    created_at: datetime
    updated_at: datetime
    chat_count: int = 0
    like_count: int = 0
    manner_temp: float = 36.5
    is_liked: bool = False


class LikeResponse(BaseModel):
    is_liked: bool
    like_count: int


class UpdatePostRequest(BaseModel):
    title: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    price: int | None = Field(default=None, ge=0)
    is_free: bool | None = None
    trade_place: str | None = Field(default=None, max_length=200)
    photos: list[str] | None = Field(default=None, max_length=10)

    @model_validator(mode="after")
    def price_none_when_free(self) -> "UpdatePostRequest":
        if self.is_free and self.price is not None:
            raise ValueError("나눔 게시글은 price를 설정할 수 없습니다.")
        return self


class PostStatusRequest(BaseModel):
    status: str

    @model_validator(mode="after")
    def validate_status(self) -> "PostStatusRequest":
        if self.status not in ("판매중", "예약중"):
            raise ValueError("판매중 또는 예약중만 변경 가능합니다.")
        return self


class CompletePostRequest(BaseModel):
    buyer_email: EmailStr


class BuyerItem(BaseModel):
    buyer_email: str


class BuyersResponse(BaseModel):
    buyers: list[BuyerItem]


class SaveDraftRequest(BaseModel):
    title: str = Field(default="", max_length=100)
    description: str = Field(default="", max_length=2000)
    price: int | None = Field(default=None, ge=0)
    is_free: bool = False
    trade_place: str | None = None
    photos: list[str] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def price_none_when_free(self) -> "SaveDraftRequest":
        if self.is_free and self.price is not None:
            raise ValueError("나눔 게시글은 price를 설정할 수 없습니다.")
        return self


class MyPostsResponse(BaseModel):
    items: list[PostListItem]
    total: int


class PurchaseItem(BaseModel):
    id: int
    title: str
    thumbnail: str | None
    price: int | None
    is_free: bool
    updated_at: datetime


class PurchasesResponse(BaseModel):
    items: list[PurchaseItem]
    total: int


class DraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    price: int | None
    is_free: bool
    trade_place: str | None
    photos: list[str]
    updated_at: datetime
