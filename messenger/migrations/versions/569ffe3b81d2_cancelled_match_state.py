"""Add CANCELLED match status

Revision ID: 569ffe3b81d2
Revises: 4a0150ad6b47
Create Date: 2024-04-01 17:28:06.264851

"""

import sqlalchemy as sa
from alembic import op

revision: str = "569ffe3b81d2"
down_revision: str | None = "4a0150ad6b47"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute(sa.text("ALTER type matchstates ADD VALUE 'CANCELLED'"))


def downgrade() -> None: ...
