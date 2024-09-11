"""Add is_closed column to the chats table

Revision ID: 183b255af081
Revises: 3a35cbc63cfe
Create Date: 2023-07-24 07:56:03.692717

"""

import sqlalchemy as sa
from alembic import op

revision: str = "183b255af081"
down_revision: str | None = "3a35cbc63cfe"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("chats", sa.Column("is_closed", sa.Boolean(), nullable=True))
    op.execute(sa.text("UPDATE chats SET is_closed = false"))
    op.alter_column("chats", "is_closed", nullable=False)


def downgrade() -> None:
    op.drop_column("chats", "is_closed")
