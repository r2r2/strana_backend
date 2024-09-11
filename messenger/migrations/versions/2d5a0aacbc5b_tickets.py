"""Add tickets and related tables

Revision ID: 2d5a0aacbc5b
Revises: d2b07084c088
Create Date: 2023-03-28 20:37:08.236294

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2d5a0aacbc5b"
down_revision: str | None = "d2b07084c088"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None

ticket_statuses = postgresql.ENUM("NEW", "IN_PROGRESS", "SOLVED", name="ticketstatuses", create_type=False)


def upgrade() -> None:
    ticket_statuses.create(bind=op.get_bind())
    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("status", ticket_statuses, nullable=False),
        sa.Column("assigned_to_user_id", sa.Integer(), nullable=True),
        sa.Column("created_from_chat_id", sa.Integer(), nullable=True),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column("comment", sa.String(length=2000), nullable=True),
        sa.Column(
            "close_reason",
            postgresql.ENUM("NO_SOLUTION_REQUIRED", "TECHNICAL_PROBLEM_SOLVED", name="ticketclosereasons"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ticket_status_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("new_status", ticket_statuses, nullable=False),
        sa.Column("updated_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["ticket_id"],
            ["tickets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("ticket_status_logs")
    op.drop_table("tickets")
    ticket_statuses.drop(bind=op.get_bind())
