from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cities_city" ADD "latitude" DECIMAL(9,6);
        ALTER TABLE "cities_city" ADD "longitude" DECIMAL(9,6);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cities_city" DROP COLUMN "latitude";
        ALTER TABLE "cities_city" DROP COLUMN "longitude";"""
