"""Rename scout_num to scout_number

Revision ID: 44137169f706
Revises: 986b8992e478
Create Date: 2023-07-26 15:52:23.657265

"""

import sqlalchemy as sa
from alembic import op

revision: str = "44137169f706"
down_revision: str | None = "986b8992e478"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("match_scouts", sa.Column("scout_number", sa.Integer(), nullable=False))
    op.drop_constraint("unique_match_scouts_match_scout", "match_scouts", type_="unique")
    op.create_unique_constraint(
        "unique_match_scouts_scout_number_match_id",
        "match_scouts",
        ["sportlevel_match_id", "scout_number"],
    )
    op.drop_column("match_scouts", "scout_id")
    op.add_column("users", sa.Column("scout_number", sa.Integer(), nullable=True))
    op.drop_column("users", "scout_num")


def downgrade() -> None:
    op.add_column("users", sa.Column("scout_num", sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column("users", "scout_number")
    op.add_column("match_scouts", sa.Column("scout_id", sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint("unique_match_scouts_scout_number_match_id", "match_scouts", type_="unique")
    op.create_unique_constraint("unique_match_scouts_match_scout", "match_scouts", ["sportlevel_match_id", "scout_id"])
    op.drop_column("match_scouts", "scout_number")
