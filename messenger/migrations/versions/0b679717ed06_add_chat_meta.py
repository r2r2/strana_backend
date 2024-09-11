"""Add chat meta

Revision ID: 0b679717ed06
Revises: ceb3435a0219
Create Date: 2023-06-22 10:02:43.410426

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0b679717ed06"
down_revision: str | None = "ceb3435a0219"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("chats", sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=False))


def downgrade() -> None:
    op.drop_column("chats", "meta")
