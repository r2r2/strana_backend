"""Add users table

Revision ID: 986b8992e478
Revises: 183b255af081
Create Date: 2023-07-24 16:29:36.549361

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "986b8992e478"
down_revision: str | None = "183b255af081"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute(sa.text("truncate table match_scouts restart identity cascade;"))
    op.execute(sa.text("truncate table matches restart identity cascade;"))
    op.create_table(
        "users",
        sa.Column("sportlevel_id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("scout_num", sa.Integer(), nullable=True),
        sa.Column(
            "role",
            postgresql.ENUM("SCOUT", "BOOKMAKER", "SUPERVISOR", name="user_roles", create_type=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("sportlevel_id"),
    )
    op.create_index(op.f("ix_users_sportlevel_id"), "users", ["sportlevel_id"], unique=False)
    op.drop_column("match_scouts", "scout_name")
    op.drop_column("match_scouts", "scout_number")


def downgrade() -> None:
    op.add_column("match_scouts", sa.Column("scout_number", sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column("match_scouts", sa.Column("scout_name", sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.drop_index(op.f("ix_users_sportlevel_id"), table_name="users")
    op.drop_table("users")
