from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_user" ADD "loyalty_status_level_icon" VARCHAR(300);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_user" DROP COLUMN "loyalty_status_level_icon";"""
