"""Add old_status

Revision ID: 74d8339def33
Revises: 614d91f4c82f
Create Date: 2023-11-17 14:30:30.954058

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "74d8339def33"
down_revision: str | None = "614d91f4c82f"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "ticket_status_logs",
        sa.Column(
            "old_status",
            postgresql.ENUM(name="ticketstatuses", create_type=False),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("ticket_status_logs", "old_status")
