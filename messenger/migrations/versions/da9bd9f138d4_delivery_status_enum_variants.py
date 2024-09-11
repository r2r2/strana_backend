"""Update delivery status enum variants

Revision ID: da9bd9f138d4
Revises: b0626c83f685
Create Date: 2023-10-17 15:39:42.605526

"""

import sqlalchemy as sa
from alembic import op

revision: str = "da9bd9f138d4"
down_revision: str | None = "b0626c83f685"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            "ALTER TYPE delivery_statuses ADD VALUE 'PENDING' BEFORE 'NOT_DELIVERED'",
        ),
    )
    op.execute(
        sa.text(
            "ALTER TYPE delivery_statuses RENAME VALUE 'NOT_DELIVERED' TO 'SENT'",
        ),
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "ALTER TYPE delivery_statuses RENAME VALUE 'SENT' TO 'NOT_DELIVERED'",
        ),
    )
    op.execute(
        sa.text(
            "UPDATE messages SET delivery_status = 'NOT_DELIVERED' WHERE delivery_status = 'PENDING'",
        ),
    )
    op.execute(
        sa.text(
            "ALTER TYPE delivery_statuses RENAME VALUE 'PENDING' TO 'DELETED'",
        ),
    )
