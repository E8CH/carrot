from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


class SourceItem(BaseModel):
    source_type: str
    source_id: str
    content: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceItem]


class IndexDocsResponse(BaseModel):
    indexed: int

class IndexPostsResponse(BaseModel):
    indexed: int
