from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_booking" ADD "price_offer_id" INT;
        ALTER TABLE "booking_booking" ADD CONSTRAINT "fk_booking__payments_a0d9ad28" FOREIGN KEY ("price_offer_id") REFERENCES "payments_price_offer_matrix" ("id") ON DELETE SET NULL;
        
        DROP TABLE IF EXISTS "payments_price_import_matrix_cities";
        DROP TABLE IF EXISTS "payments_price_import_matrix";
        DROP TABLE IF EXISTS "payments_price_schema";
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_booking" DROP CONSTRAINT "fk_booking__payments_a0d9ad28";
        ALTER TABLE "booking_booking" DROP COLUMN "price_offer_id";
    
        CREATE TABLE IF NOT EXISTS "payments_price_schema" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "slug" VARCHAR(15)  UNIQUE,
            "price_type_id" INT NOT NULL REFERENCES "payments_property_price_type" ("id") ON DELETE CASCADE
        );
        COMMENT ON COLUMN "payments_price_schema"."id" IS 'ID';
        COMMENT ON COLUMN "payments_price_schema"."slug" IS 'slug поля цены из Profit base';
        COMMENT ON COLUMN "payments_price_schema"."price_type_id" IS 'Тип цены';
        COMMENT ON TABLE "payments_price_schema" IS 'Схема сопоставление цен в матрице';
        CREATE TABLE IF NOT EXISTS "payments_price_import_matrix" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "default" BOOL NOT NULL  DEFAULT False,
            "price_schema_id" INT NOT NULL REFERENCES "payments_price_schema" ("id") ON DELETE CASCADE
        );
        COMMENT ON COLUMN "payments_price_import_matrix"."id" IS 'ID';
        COMMENT ON COLUMN "payments_price_import_matrix"."default" IS 'По умолчанию';
        COMMENT ON COLUMN "payments_price_import_matrix"."price_schema_id" IS 'Сопоставление цен';
        COMMENT ON TABLE "payments_price_import_matrix" IS 'Матрица сопоставления цен при импорте объекта';
        CREATE TABLE "payments_price_import_matrix_cities" (
            import_price_id INT NOT NULL REFERENCES "payments_price_import_matrix" ("id") ON DELETE CASCADE,
            city_id INT NOT NULL REFERENCES "cities_city" ("id") ON DELETE CASCADE
        );

        COMMENT ON COLUMN "payments_price_import_matrix"."id" IS 'ID';
        COMMENT ON COLUMN "payments_price_import_matrix"."default" IS 'По умолчанию';
        COMMENT ON COLUMN "payments_price_import_matrix"."price_schema_id" IS 'Сопоставление цен';
        COMMENT ON TABLE "payments_price_import_matrix" IS 'Матрица сопоставления цен при импорте объекта';
        """
