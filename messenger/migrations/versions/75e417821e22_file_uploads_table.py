"""Add file uploads table

Revision ID: 75e417821e22
Revises: cf87a0653d20
Create Date: 2023-08-10 18:01:52.332941

"""

import sqlalchemy as sa
from alembic import op

revision: str = "75e417821e22"
down_revision: str | None = "cf87a0653d20"
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "file_uploads",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("subfolder_path", sa.String(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_file_uploads_slug"), "file_uploads", ["slug"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_file_uploads_slug"), table_name="file_uploads")
    op.drop_table("file_uploads")
