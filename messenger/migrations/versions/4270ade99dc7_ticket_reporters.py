"""Add ticket reporters table

Revision ID: 4270ade99dc7
Revises: 2d5a0aacbc5b
Create Date: 2023-03-29 15:22:16.963234

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "4270ade99dc7"
down_revision: str | None = "2d5a0aacbc5b"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "ticket_reporters",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("user_role", postgresql.ENUM(name="user_roles", create_type=False), nullable=False),
        sa.ForeignKeyConstraint(
            ["ticket_id"],
            ["tickets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ticket_reporters_ticket_id"), "ticket_reporters", ["ticket_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ticket_reporters_ticket_id"), table_name="ticket_reporters")
    op.drop_table("ticket_reporters")
