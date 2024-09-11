"""Add user_role column to the chat_membership table

Revision ID: c06083ea0a2f
Revises: 8cb3366e98fd
Create Date: 2023-03-13 15:17:16.724340

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c06083ea0a2f"
down_revision: str | None = "8cb3366e98fd"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    user_roles_enum = postgresql.ENUM(
        "SCOUT",
        "BOOKMAKER",
        "SUPERVISOR",
        name="user_roles",
        schema_name="public",
    )
    user_roles_enum.create(bind=op.get_bind())

    op.add_column(
        "chat_membership",
        sa.Column(
            "user_role",
            user_roles_enum,
            nullable=True,
        ),
    )
    op.execute(sa.text("update chat_membership set user_role = 'SCOUT'"))
    op.alter_column("chat_membership", "user_role", nullable=False)


def downgrade() -> None:
    op.drop_column("chat_membership", "user_role")
    postgresql.ENUM(name="user_roles").drop(bind=op.get_bind())
