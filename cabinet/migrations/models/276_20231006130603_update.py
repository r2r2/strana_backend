from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "payments_price_schema" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "slug" VARCHAR(15)  UNIQUE,
    "price_type_id" INT NOT NULL REFERENCES "payments_property_price_type" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "payments_price_schema"."id" IS 'ID';
COMMENT ON COLUMN "payments_price_schema"."slug" IS 'slug поля цены из Profit base';
COMMENT ON COLUMN "payments_price_schema"."price_type_id" IS 'Тип цены';
COMMENT ON TABLE "payments_price_schema" IS 'Схема сопоставление цен в матрице';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "payments_price_schema";"""
