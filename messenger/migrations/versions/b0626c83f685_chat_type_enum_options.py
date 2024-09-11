"""Update ChatType enum options

Revision ID: b0626c83f685
Revises: 75e417821e22
Create Date: 2023-09-15 15:16:37.813703

"""

from alembic import op

revision: str = "b0626c83f685"
down_revision: str | None = "75e417821e22"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TYPE chattypes_new AS ENUM (
            'PERSONAL',
            'MATCH',
            'TICKET'
        )
    """,
    )
    op.execute(
        """
        ALTER TABLE chats
        ALTER COLUMN type TYPE chattypes_new
        USING CASE
            WHEN type = 'NON_SPECIFIC' THEN 'PERSONAL'::chattypes_new
            WHEN type = 'BOOKMAKER_WITH_SCOUT' THEN 'MATCH'::chattypes_new
            WHEN type = 'BOOKMAKER_WITH_SUPERVISOR' THEN 'TICKET'::chattypes_new
            WHEN type = 'SCOUT_WITH_SUPERVISOR' THEN 'TICKET'::chattypes_new
        END;
        """,
    )
    op.execute("DROP TYPE chattypes")
    op.execute("ALTER TYPE chattypes_new RENAME TO chattypes")


def downgrade() -> None:
    op.execute(
        """
        CREATE TYPE chattypes_new AS ENUM (
            'NON_SPECIFIC',
            'BOOKMAKER_WITH_SCOUT',
            'BOOKMAKER_WITH_SUPERVISOR',
            'SCOUT_WITH_SUPERVISOR
        )
    """,
    )
    op.execute(
        """
        ALTER TABLE chats
        ALTER COLUMN type TYPE chattypes_new
        USING CASE
            WHEN type = 'PERSONAL' THEN 'NON_SPECIFIC'::chattypes_new
            WHEN type = 'MATCH' THEN 'BOOKMAKER_WITH_SCOUT'::chattypes_new
            WHEN type = 'TICKET' THEN 'BOOKMAKER_WITH_SUPERVISOR'::chattypes_new
        END;
        """,
    )
    op.execute("DROP TYPE chattypes")
    op.execute("ALTER TYPE chattypes_new RENAME TO chattypes")
