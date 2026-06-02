"""add embeddings table for RAG

Revision ID: 003_pgvector
Revises: 002_add_sender_email
Create Date: 2026-06-02
"""
from typing import Sequence, Union

from alembic import op

revision: str = "003_pgvector"
down_revision: Union[str, None] = "002_add_sender_email"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("""
        CREATE TABLE embeddings (
            id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
            source_type VARCHAR(20)  NOT NULL,
            source_id   VARCHAR(255) NOT NULL,
            content     TEXT         NOT NULL,
            embedding   vector(1536),
            metadata    JSONB        DEFAULT '{}',
            created_at  TIMESTAMPTZ  DEFAULT NOW()
        )
    """)
    op.execute("""
        CREATE INDEX embeddings_hnsw_idx
        ON embeddings USING hnsw (embedding vector_cosine_ops)
    """)
    op.execute(
        "CREATE INDEX embeddings_source_idx ON embeddings (source_type, source_id)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS embeddings")
