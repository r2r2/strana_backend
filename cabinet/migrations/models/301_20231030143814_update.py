from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "properties_property" ADD "profitbase_plan" VARCHAR(512);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "properties_property" DROP COLUMN "profitbase_plan";"""
