"""add sender_email to chat_messages

Revision ID: 002_add_sender_email
Revises: 001_initial
Create Date: 2026-05-31 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_add_sender_email"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "chat_messages",
        sa.Column("sender_email", sa.String(255), nullable=True),
    )
    op.execute("UPDATE chat_messages SET sender_email = buyer_email WHERE sender_email IS NULL")
    op.alter_column("chat_messages", "sender_email", nullable=False)
    op.create_foreign_key(
        "fk_chat_messages_sender_email",
        "chat_messages",
        "users",
        ["sender_email"],
        ["email"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_chat_messages_sender_email", "chat_messages", type_="foreignkey")
    op.drop_column("chat_messages", "sender_email")
