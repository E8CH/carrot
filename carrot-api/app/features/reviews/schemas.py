from datetime import datetime

from pydantic import BaseModel, Field


class CreateReviewRequest(BaseModel):
    post_id: int = Field(ge=1)
    is_positive: bool
    tags: list[str] = Field(default_factory=list)
    comment: str | None = Field(default=None, max_length=500)


class ReviewResponse(BaseModel):
    id: int
    post_id: int
    writer_email: str
    target_email: str
    is_positive: bool
    tags: list[str]
    comment: str | None
    created_at: datetime
