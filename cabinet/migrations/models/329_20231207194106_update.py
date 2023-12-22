from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "properties_property" ADD "profitbase_id" INT  UNIQUE;
        CREATE UNIQUE INDEX "uid_properties__profitb_9e11b7" ON "properties_property" ("profitbase_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "uid_properties__profitb_9e11b7";
        ALTER TABLE "properties_property" DROP COLUMN "profitbase_id";"""
