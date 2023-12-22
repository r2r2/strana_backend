from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "dashboard_element" ADD COLUMN IF NOT EXISTS "enable_fos" BOOL NOT NULL  DEFAULT False;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "dashboard_element" DROP COLUMN IF EXISTS "enable_fos";
        """
