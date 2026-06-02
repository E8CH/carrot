from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.rag.schemas import ChatRequest, ChatResponse, IndexDocsResponse, IndexPostsResponse, SourceItem
from app.features.rag.service import rag_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    answer, contexts = await rag_service.chat(db, request.message)
    sources = [
        SourceItem(
            source_type=c["source_type"],
            source_id=c["source_id"],
            content=c["content"][:300],
        )
        for c in contexts
    ]
    return ChatResponse(answer=answer, sources=sources)


@router.post("/index-docs", response_model=IndexDocsResponse)
async def index_docs(
    db: AsyncSession = Depends(get_db),
) -> IndexDocsResponse:
    count = await rag_service.index_docs(db)
    return IndexDocsResponse(indexed=count)


@router.post("/index-posts", response_model=IndexPostsResponse)
async def index_posts(
    db: AsyncSession = Depends(get_db),
) -> IndexPostsResponse:
    count = await rag_service.index_all_posts(db)
    return IndexPostsResponse(indexed=count)
