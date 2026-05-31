"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-05-29 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users 테이블
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("address", sa.String(500), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("role", sa.String(10), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("manner_temp", sa.Float(), nullable=False, server_default="36.5"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # posts 테이블
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("seller_email", sa.String(255), nullable=False),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=True),
        sa.Column("is_free", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status", sa.String(10), nullable=False, server_default="판매중"),
        sa.Column("trade_place", sa.String(200), nullable=True),
        sa.Column("photos", postgresql.ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("buyer_email", sa.String(255), nullable=True),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_draft", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["seller_email"], ["users.email"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["buyer_email"], ["users.email"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_posts_seller_email", "posts", ["seller_email"])

    # chat_messages 테이블
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("room_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("seller_email", sa.String(255), nullable=False),
        sa.Column("buyer_email", sa.String(255), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["seller_email"], ["users.email"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["buyer_email"], ["users.email"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_messages_room_id", "chat_messages", ["room_id"])
    # AR-3: 채팅 폴링 성능을 위한 복합 인덱스 (SM-C1 준수)
    op.create_index(
        "idx_chat_messages_post_id_sent_at",
        "chat_messages",
        ["post_id", "sent_at"],
    )

    # likes 테이블
    op.create_table(
        "likes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_email", sa.String(255), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_email"], ["users.email"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_email", "post_id", name="uq_likes_user_post"),
    )

    # reviews 테이블
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("writer_email", sa.String(255), nullable=False),
        sa.Column("target_email", sa.String(255), nullable=False),
        sa.Column("is_positive", sa.Boolean(), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("post_id", "writer_email", name="uq_reviews_post_writer"),
    )


def downgrade() -> None:
    op.drop_table("reviews")
    op.drop_table("likes")
    op.drop_index("idx_chat_messages_post_id_sent_at", table_name="chat_messages")
    op.drop_index("ix_chat_messages_room_id", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_index("ix_posts_seller_email", table_name="posts")
    op.drop_table("posts")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
