from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "properties_property" DROP CONSTRAINT IF EXISTS "fk_properti_payments_be8c8572";
        ALTER TABLE "properties_property" DROP COLUMN IF EXISTS "property_price_id";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "properties_property" ADD "property_price_id" INT;
        ALTER TABLE "properties_property" ADD CONSTRAINT "fk_properti_payments_be8c8572" FOREIGN KEY ("property_price_id") REFERENCES "payments_property_price" ("id") ON DELETE SET NULL;"""
