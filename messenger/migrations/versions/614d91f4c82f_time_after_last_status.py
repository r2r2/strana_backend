"""Add time_after_last_status

Revision ID: 614d91f4c82f
Revises: da9bd9f138d4
Create Date: 2023-11-17 12:29:18.120472

"""

import sqlalchemy as sa
from alembic import op

revision: str = "614d91f4c82f"
down_revision: str | None = "da9bd9f138d4"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "ticket_status_logs", sa.Column("time_after_last_status", sa.Integer(), nullable=True, comment="in seconds")
    )
    op.execute(sa.text("UPDATE ticket_status_logs SET time_after_last_status = 0"))
    op.alter_column("ticket_status_logs", "time_after_last_status", nullable=False)


def downgrade() -> None:
    op.drop_column("ticket_status_logs", "time_after_last_status")
