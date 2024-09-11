"""Add CONFIRMED ticket status

Revision ID: 4a262dc7d785
Revises: 0b679717ed06
Create Date: 2023-07-20 13:54:57.578298

"""

import sqlalchemy as sa
from alembic import op

revision: str = "4a262dc7d785"
down_revision: str | None = "0b679717ed06"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute(sa.text("alter type ticketstatuses add value 'CONFIRMED'"))


def downgrade() -> None:
    op.execute(sa.text("DELETE from tickets where status = 'CONFIRMED':ticketstatuses"))
