"""Add is_primary_member column to chat_membership

Revision ID: 281d69798ed2
Revises: ed1d7abd6881
Create Date: 2023-03-23 11:15:02.472566

"""

import sqlalchemy as sa
from alembic import op

revision: str = "281d69798ed2"
down_revision: str | None = "ed1d7abd6881"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("chat_membership", sa.Column("is_primary_member", sa.Boolean(), nullable=True))
    op.execute(sa.text("update chat_membership set is_primary_member = true"))
    op.alter_column("chat_membership", "is_primary_member", nullable=False)


def downgrade() -> None:
    op.drop_column("chat_membership", "is_primary_member")
