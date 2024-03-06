from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "properties_property" ADD "plan_hover" TEXT;
        ALTER TABLE "floors_floor" ADD "plan" VARCHAR(500);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "floors_floor" DROP COLUMN "plan";
        ALTER TABLE "properties_property" DROP COLUMN "plan_hover";"""
