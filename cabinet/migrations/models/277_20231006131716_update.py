from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "payments_price_import_matrix" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "default" BOOL NOT NULL  DEFAULT False,
    "price_schema_id" INT NOT NULL REFERENCES "payments_price_schema" ("id") ON DELETE CASCADE
);

CREATE TABLE "payments_price_import_matrix_cities" (
    import_price_id INT NOT NULL REFERENCES "payments_price_import_matrix" ("id") ON DELETE CASCADE,
    city_id INT NOT NULL REFERENCES "cities_city" ("id") ON DELETE CASCADE
);

COMMENT ON COLUMN "payments_price_import_matrix"."id" IS 'ID';
COMMENT ON COLUMN "payments_price_import_matrix"."default" IS 'По умолчанию';
COMMENT ON COLUMN "payments_price_import_matrix"."price_schema_id" IS 'Сопоставление цен';
COMMENT ON TABLE "payments_price_import_matrix" IS 'Матрица сопоставления цен при импорте объекта';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "payments_price_import_matrix_cities";
        DROP TABLE IF EXISTS "payments_price_import_matrix";
        """
