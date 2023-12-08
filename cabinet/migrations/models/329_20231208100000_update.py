from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "dashboard_element" ADD COLUMN IF NOT EXISTS "priority" INT NOT NULL  DEFAULT 0;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "dashboard_element" DROP COLUMN IF EXISTS "priority";
        """
