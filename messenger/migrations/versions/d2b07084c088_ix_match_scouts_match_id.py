"""Add index ix_match_scouts_match_id

Revision ID: d2b07084c088
Revises: 281d69798ed2
Create Date: 2023-03-27 17:21:22.539495

"""

from alembic import op

revision: str = "d2b07084c088"
down_revision: str | None = "281d69798ed2"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_index("ix_match_scouts_match_id", "match_scouts", ["sportlevel_match_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_match_scouts_match_id", table_name="match_scouts")
