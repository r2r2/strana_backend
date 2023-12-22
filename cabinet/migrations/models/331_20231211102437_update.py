from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "properties_property" DROP COLUMN "profitbase_id";
        ALTER TABLE "properties_property" ADD "profitbase_id" INT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "properties_property" DROP COLUMN "profitbase_id";
        ALTER TABLE "properties_property" ADD "profitbase_id" INT;"""
