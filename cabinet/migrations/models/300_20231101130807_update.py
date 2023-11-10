from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_user" RENAME COLUMN "is_ready_for_authorisation_by_superuser" TO "ready_for_super_auth";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_user" RENAME COLUMN "ready_for_super_auth" TO "is_ready_for_authorisation_by_superuser";"""
