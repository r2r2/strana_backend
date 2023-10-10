from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "main_page_manager" ADD "position" VARCHAR(512);
        ALTER TABLE "main_page_manager" ADD "photo" VARCHAR(2000);
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "main_page_manager" DROP COLUMN "position";
        ALTER TABLE "main_page_manager" DROP COLUMN "photo";
    """
