"""Add state column to matches

Revision ID: 3a35cbc63cfe
Revises: 4a262dc7d785
Create Date: 2023-07-21 16:42:19.378105

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "3a35cbc63cfe"
down_revision: str | None = "4a262dc7d785"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None

match_state_enum = postgresql.ENUM("ACTIVE", "ARCHIVED", name="matchstates", create_type=False)


def upgrade() -> None:
    match_state_enum.create(op.get_bind())
    op.add_column(
        "matches",
        sa.Column("state", match_state_enum, nullable=True),
    )
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE matches SET state = :state"), {"state": "ACTIVE"})
    op.alter_column("matches", "state", nullable=False)


def downgrade() -> None:
    op.drop_column("matches", "state")
