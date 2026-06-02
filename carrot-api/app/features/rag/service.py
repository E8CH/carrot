import re
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

_DOCS_DIR = Path(__file__).parent.parent.parent.parent / "rag-docs"
_EMBED_MODEL = "text-embedding-3-small"
_CHAT_MODEL = "gpt-4o-mini"
_TOP_K = 5

_SYSTEM_PROMPT = """당신은 carrot 중고거래 플랫폼의 도움말 챗봇입니다.
아래에 제공된 참고 자료를 바탕으로 사용자의 질문에 친절하고 간결하게 답변하세요.

규칙:
- 반드시 한국어로 답변하세요.
- 참고 자료에 없는 내용은 "확인이 어렵습니다. 고객센터에 문의해 주세요."라고 답변하세요.
- 게시글 관련 질문(특정 상품, 가격 등)은 참고 자료의 게시글 정보를 기반으로 답변하세요.
- 답변은 2~4문장으로 간결하게 작성하세요."""


class RagService:
    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    async def _embed(self, content: str) -> list[float]:
        result = await self._get_client().embeddings.create(
            input=content, model=_EMBED_MODEL
        )
        return result.data[0].embedding

    @staticmethod
    def _vec_str(embedding: list[float]) -> str:
        return "[" + ",".join(str(x) for x in embedding) + "]"

    async def search(self, db: AsyncSession, query: str) -> list[dict[str, Any]]:
        vec = await self._embed(query)
        rows = await db.execute(
            text("""
                SELECT source_type, source_id, content, metadata
                FROM embeddings
                ORDER BY embedding <=> CAST(:vec AS vector)
                LIMIT :k
            """),
            {"vec": self._vec_str(vec), "k": _TOP_K},
        )
        return [dict(r._mapping) for r in rows.fetchall()]

    async def chat(self, db: AsyncSession, message: str) -> tuple[str, list[dict]]:
        contexts = await self.search(db, message)
        context_text = "\n\n---\n\n".join(
            f"[출처: {c['source_type']} / {c['source_id']}]\n{c['content']}"
            for c in contexts
        )
        response = await self._get_client().chat.completions.create(
            model=_CHAT_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"참고 자료:\n{context_text}\n\n질문: {message}",
                },
            ],
            max_tokens=1024,
        )
        answer = response.choices[0].message.content or ""
        return answer, contexts

    async def index_post(
        self,
        db: AsyncSession,
        post_id: int,
        title: str,
        description: str,
        trade_place: str | None,
    ) -> None:
        content = f"제목: {title}\n\n설명: {description}"
        if trade_place:
            content += f"\n\n거래 희망 장소: {trade_place}"
        vec = await self._embed(content)
        await db.execute(
            text("DELETE FROM embeddings WHERE source_type = 'post' AND source_id = :sid"),
            {"sid": str(post_id)},
        )
        await db.execute(
            text("""
                INSERT INTO embeddings (source_type, source_id, content, embedding)
                VALUES ('post', :sid, :content, CAST(:vec AS vector))
            """),
            {"sid": str(post_id), "content": content, "vec": self._vec_str(vec)},
        )
        await db.commit()

    async def delete_post_embedding(self, db: AsyncSession, post_id: int) -> None:
        await db.execute(
            text("DELETE FROM embeddings WHERE source_type = 'post' AND source_id = :sid"),
            {"sid": str(post_id)},
        )
        await db.commit()

    def _chunk_markdown(self, raw: str, filename: str) -> list[dict[str, str]]:
        sections = re.split(r"\n(?=## )", raw)
        return [
            {"source_id": filename, "content": s.strip()}
            for s in sections
            if len(s.strip()) >= 50
        ]

    async def index_all_posts(self, db: AsyncSession) -> int:
        from sqlalchemy import select
        from app.features.posts.models import Post

        rows = (await db.execute(
            select(Post).where(Post.is_draft == False)  # noqa: E712
        )).scalars().all()

        await db.execute(text("DELETE FROM embeddings WHERE source_type = 'post'"))
        await db.commit()

        for post in rows:
            content = f"제목: {post.title}\n\n설명: {post.description}"
            if post.trade_place:
                content += f"\n\n거래 희망 장소: {post.trade_place}"
            vec = await self._embed(content)
            await db.execute(
                text("""
                    INSERT INTO embeddings (source_type, source_id, content, embedding)
                    VALUES ('post', :sid, :content, CAST(:vec AS vector))
                """),
                {"sid": str(post.id), "content": content, "vec": self._vec_str(vec)},
            )
        await db.commit()
        return len(rows)

    async def index_docs(self, db: AsyncSession) -> int:
        if not _DOCS_DIR.exists():
            return 0
        await db.execute(text("DELETE FROM embeddings WHERE source_type = 'doc'"))
        await db.commit()
        total = 0
        for md_file in sorted(_DOCS_DIR.glob("*.md")):
            chunks = self._chunk_markdown(
                md_file.read_text(encoding="utf-8"), md_file.name
            )
            for chunk in chunks:
                vec = await self._embed(chunk["content"])
                await db.execute(
                    text("""
                        INSERT INTO embeddings (source_type, source_id, content, embedding)
                        VALUES ('doc', :sid, :content, CAST(:vec AS vector))
                    """),
                    {
                        "sid": chunk["source_id"],
                        "content": chunk["content"],
                        "vec": self._vec_str(vec),
                    },
                )
                total += 1
        await db.commit()
        return total


rag_service = RagService()
