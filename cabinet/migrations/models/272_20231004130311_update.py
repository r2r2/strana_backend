from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_amocrm_checks_history_log" ALTER COLUMN "query" DROP NOT NULL;
        ALTER TABLE "users_amocrm_checks_history_log" RENAME COLUMN "query" TO "request_data";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_amocrm_checks_history_log" RENAME COLUMN "request_data" TO "query";
        ALTER TABLE "users_amocrm_checks_history_log" ALTER COLUMN "query" SET NOT NULL;"""
