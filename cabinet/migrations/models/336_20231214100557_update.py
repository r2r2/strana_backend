from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_client_assign_maintenance" ADD "broker_amocrm_id" BIGINT NOT NULL;
        ALTER TABLE "users_client_check_maintenance" ADD "broker_amocrm_id" BIGINT NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_client_check_maintenance" DROP COLUMN "broker_amocrm_id";
        ALTER TABLE "users_client_assign_maintenance" DROP COLUMN "broker_amocrm_id";"""
