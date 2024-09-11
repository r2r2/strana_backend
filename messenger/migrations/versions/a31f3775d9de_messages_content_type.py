"""Messages content type

Revision ID: a31f3775d9de
Revises: 4270ade99dc7
Create Date: 2023-04-14 12:32:29.783822

"""

import sqlalchemy as sa
from alembic import op

revision: str = "a31f3775d9de"
down_revision: str | None = "4270ade99dc7"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute(sa.text("DELETE FROM MESSAGES"))
    op.execute(sa.text("ALTER TABLE MESSAGES ALTER COLUMN content TYPE BYTEA USING content::BYTEA"))


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM MESSAGES"))
    op.execute(sa.text("ALTER TABLE MESSAGES ALTER COLUMN content TYPE VARCHAR(5000) USING content::VARCHAR(5000)"))
