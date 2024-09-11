"""Nullable sender_id in messages table

Revision ID: ceb3435a0219
Revises: a31f3775d9de
Create Date: 2023-04-14 14:36:30.530940

"""

import sqlalchemy as sa
from alembic import op

revision: str = "ceb3435a0219"
down_revision: str | None = "a31f3775d9de"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.alter_column("messages", "sender_id", existing_type=sa.INTEGER(), nullable=True)


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM messages WHERE sender_id IS NULL"))
    op.alter_column("messages", "sender_id", existing_type=sa.INTEGER(), nullable=False)
