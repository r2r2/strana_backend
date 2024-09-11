"""Add permissions flag to the chat_membership table

Revision ID: 834723f41623
Revises: c06083ea0a2f
Create Date: 2023-03-15 18:08:08.001209

"""

import sqlalchemy as sa
from alembic import op

revision: str = "834723f41623"
down_revision: str | None = "c06083ea0a2f"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("chat_membership", sa.Column("has_write_permission", sa.Boolean(), nullable=True))
    op.add_column("chat_membership", sa.Column("has_read_permission", sa.Boolean(), nullable=True))

    op.execute(sa.text("update chat_membership set has_write_permission = true, has_read_permission = true"))

    op.alter_column("chat_membership", "has_read_permission", nullable=False)
    op.alter_column("chat_membership", "has_write_permission", nullable=False)


def downgrade() -> None:
    op.drop_column("chat_membership", "has_read_permission")
    op.drop_column("chat_membership", "has_write_permission")
