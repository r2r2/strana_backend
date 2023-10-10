from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_checks" ADD "send_rop_email" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "users_checks_terms" ADD "send_rop_email" BOOL NOT NULL  DEFAULT False;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_checks" DROP COLUMN "send_rop_email";
        ALTER TABLE "users_checks_terms" DROP COLUMN "send_rop_email";"""
