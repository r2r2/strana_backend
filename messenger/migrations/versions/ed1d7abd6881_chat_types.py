"""Add type column to chats

Revision ID: ed1d7abd6881
Revises: 2b5cbf2b1fd4
Create Date: 2023-03-22 15:08:45.540930

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "ed1d7abd6881"
down_revision: str | None = "2b5cbf2b1fd4"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None

chat_types_enum = postgresql.ENUM(
    "NON_SPECIFIC",
    "BOOKMAKER_WITH_SCOUT",
    "BOOKMAKER_WITH_SUPERVISOR",
    "SCOUT_WITH_SUPERVISOR",
    name="chattypes",
    create_type=False,
)


def upgrade() -> None:
    chat_types_enum.create(bind=op.get_bind())

    op.add_column(
        "chats",
        sa.Column(
            "type",
            chat_types_enum,
            nullable=True,
        ),
    )
    op.execute(sa.text("update chats set type = 'NON_SPECIFIC'"))
    op.alter_column("chats", "type", nullable=False)


def downgrade() -> None:
    op.drop_column("chats", "type")
    chat_types_enum.drop(bind=op.get_bind())
