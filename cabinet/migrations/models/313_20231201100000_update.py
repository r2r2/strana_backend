from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "client_amocrm_group_statuses" ADD COLUMN IF NOT EXISTS "is_hide" BOOL NOT NULL  DEFAULT False;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "client_amocrm_group_statuses" DROP COLUMN IF EXISTS "is_hide";
        """
