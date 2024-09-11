"""Add push_notification_configs table

Revision ID: 633fd01bef2c
Revises: 74d8339def33
Create Date: 2024-01-23 15:32:52.260375

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "633fd01bef2c"
down_revision: str | None = "74d8339def33"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "push_notification_configs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False),
        sa.Column("keys", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_unique_constraint(
        "push_notification_configs_user_id_endpoint_unique", "push_notification_configs", ["user_id", "endpoint"]
    )


def downgrade() -> None:
    op.drop_constraint("push_notification_configs_user_id_endpoint_unique", "push_notification_configs", type_="unique")
    op.drop_table("push_notification_configs")
