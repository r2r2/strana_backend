from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
            ALTER TABLE "users_user" ADD "reset_password_link" VARCHAR(200);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
            ALTER TABLE "users_user" DROP COLUMN "reset_password_link";"""
