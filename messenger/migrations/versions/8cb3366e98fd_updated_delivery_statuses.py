"""Updated delivery statuses

Revision ID: 8cb3366e98fd
Revises: 43695afb59c9
Create Date: 2023-03-07 18:13:15.656355

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "8cb3366e98fd"
down_revision: str | None = "43695afb59c9"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute(sa.text("truncate chats RESTART IDENTITY CASCADE;"))
    op.execute(sa.text("truncate messages RESTART IDENTITY CASCADE;"))
    op.execute(sa.text("truncate chat_membership RESTART IDENTITY CASCADE;"))

    op.drop_table("message_delivery_statuses")
    op.drop_index("ix_messages_id", table_name="messages")
    op.add_column("chat_membership", sa.Column("last_received_message_id", sa.BigInteger(), nullable=False))
    op.add_column("chat_membership", sa.Column("last_read_message_id", sa.BigInteger(), nullable=False))
    op.create_index("ix_chat_membership_chat_id", "chat_membership", ["chat_id"], unique=False)
    op.add_column(
        "messages",
        sa.Column(
            "delivery_status",
            postgresql.ENUM(
                "NOT_DELIVERED",
                "DELIVERED",
                "READ",
                name="delivery_statuses",
                schema="public",
                create_type=False,
            ),
            nullable=False,
        ),
    )
    op.create_index("ix_messages_chat_id", "messages", ["chat_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_messages_chat_id", table_name="messages")
    op.drop_column("messages", "delivery_status")
    op.drop_index("ix_chat_membership_chat_id", table_name="chat_membership")
    op.drop_column("chat_membership", "last_read_message_id")
    op.drop_column("chat_membership", "last_received_message_id")
    op.create_table(
        "message_delivery_statuses",
        sa.Column("id", sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column("message_id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM("NOT_DELIVERED", "DELIVERED", "READ", name="delivery_statuses", create_type=False),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], name="message_delivery_statuses_message_id_fkey"),
        sa.PrimaryKeyConstraint("id", name="message_delivery_statuses_pkey"),
        sa.UniqueConstraint("message_id", "user_id", name="message_delivery_statuses_unique"),
    )
    op.create_index("ix_messages_id", "messages", ["id"], unique=False)
