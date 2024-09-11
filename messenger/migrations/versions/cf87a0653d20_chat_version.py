"""Add version, updated_at columns to chats

Revision ID: cf87a0653d20
Revises: 57aac0ddb895
Create Date: 2023-08-02 14:39:39.206709

"""

import sqlalchemy as sa
from alembic import op

revision: str = "cf87a0653d20"
down_revision: str | None = "57aac0ddb895"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("chats", sa.Column("version", sa.Integer(), server_default="0", nullable=True))
    op.add_column("chats", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
    op.execute(sa.text("update chats set version = 0;"))
    op.alter_column("chats", "version", nullable=False)


def downgrade() -> None:
    op.drop_column("chats", "updated_at")
    op.drop_column("chats", "version")
