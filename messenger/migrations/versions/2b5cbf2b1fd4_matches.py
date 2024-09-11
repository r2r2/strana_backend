"""Indexes and matches table

Revision ID: 2b5cbf2b1fd4
Revises: 834723f41623
Create Date: 2023-03-17 13:00:17.035115

"""

import sqlalchemy as sa
from alembic import op

revision: str = "2b5cbf2b1fd4"
down_revision: str | None = "834723f41623"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("chats", sa.Column("match_id", sa.Integer(), nullable=True))
    op.create_table(
        "match_scouts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("sportlevel_match_id", sa.Integer(), nullable=False),
        sa.Column("scout_id", sa.Integer(), nullable=False),
        sa.Column("is_main_scout", sa.Boolean(), nullable=False),
        sa.Column("scout_number", sa.Integer(), nullable=True),
        sa.Column("scout_name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sportlevel_match_id", "scout_id", name="unique_match_scouts_match_scout"),
    )
    op.create_index(op.f("ix_match_scouts_sportlevel_match_id"), "match_scouts", ["sportlevel_match_id"], unique=False)
    op.create_table(
        "matches",
        sa.Column("sportlevel_id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finish_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sport_id", sa.Integer(), nullable=False),
        sa.Column("team_a_id", sa.Integer(), nullable=False),
        sa.Column("team_b_id", sa.Integer(), nullable=False),
        sa.Column("team_a_name_ru", sa.Text(), nullable=False),
        sa.Column("team_a_name_en", sa.Text(), nullable=False),
        sa.Column("team_b_name_ru", sa.Text(), nullable=False),
        sa.Column("team_b_name_en", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("sportlevel_id"),
    )
    op.create_index(op.f("ix_matches_finish_at"), "matches", ["finish_at"], unique=False)
    op.create_index(op.f("ix_matches_sportlevel_id"), "matches", ["sportlevel_id"], unique=False)
    op.create_index(op.f("ix_matches_start_at"), "matches", ["start_at"], unique=False)
    op.create_index("ix_messages_last_message_search", "messages", ["chat_id", sa.text("id DESC")], unique=False)
    op.create_index("ix_chats_match_id", "chats", ["match_id"], unique=False)
    op.create_table(
        "sports",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("name_ru", sa.Text(), nullable=False),
        sa.Column("name_en", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("sports")
    op.drop_index("ix_chats_match_id", table_name="chats")
    op.drop_index("ix_messages_last_message_search", table_name="messages")
    op.drop_index(op.f("ix_matches_start_at"), table_name="matches")
    op.drop_index(op.f("ix_matches_sportlevel_id"), table_name="matches")
    op.drop_index(op.f("ix_matches_finish_at"), table_name="matches")
    op.drop_table("matches")
    op.drop_index(op.f("ix_match_scouts_sportlevel_match_id"), table_name="match_scouts")
    op.drop_table("match_scouts")
    op.drop_column("chats", "match_id")
