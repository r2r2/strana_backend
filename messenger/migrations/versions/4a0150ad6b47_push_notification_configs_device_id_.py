"""Add device_id column to the push_notification_configs table

Revision ID: 4a0150ad6b47
Revises: 633fd01bef2c
Create Date: 2024-02-14 17:55:44.292185

"""

import sqlalchemy as sa
from alembic import op

revision: str = "4a0150ad6b47"
down_revision: str | None = "633fd01bef2c"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute(sa.text("TRUNCATE TABLE push_notification_configs"))
    op.add_column("push_notification_configs", sa.Column("last_alive_at", sa.DateTime(timezone=True), nullable=False))
    op.add_column("push_notification_configs", sa.Column("device_id", sa.String(length=100), nullable=False))
    op.create_unique_constraint(
        "push_notification_configs_device_id_unique", "push_notification_configs", ["device_id"]
    )


def downgrade() -> None:
    op.drop_constraint("push_notification_configs_device_id_unique", "push_notification_configs", type_="unique")
    op.drop_column("push_notification_configs", "last_alive_at")
    op.drop_column("push_notification_configs", "device_id")
