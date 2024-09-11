"""Delete ticket_reporters table

Revision ID: 57aac0ddb895
Revises: 44137169f706
Create Date: 2023-08-01 17:39:17.610352

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "57aac0ddb895"
down_revision: str | None = "44137169f706"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.drop_index("ix_ticket_reporters_ticket_id", table_name="ticket_reporters")
    op.drop_table("ticket_reporters")


def downgrade() -> None:
    op.create_table(
        "ticket_reporters",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("ticket_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "user_role",
            postgresql.ENUM("SCOUT", "BOOKMAKER", "SUPERVISOR", name="user_roles"),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"], name="ticket_reporters_ticket_id_fkey"),
        sa.PrimaryKeyConstraint("id", name="ticket_reporters_pkey"),
    )
    op.create_index("ix_ticket_reporters_ticket_id", "ticket_reporters", ["ticket_id"], unique=False)
