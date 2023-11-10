from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
            CREATE TABLE IF NOT EXISTS "offers_offer_source" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(150) NOT NULL,
    "slug" VARCHAR(32) NOT NULL
);
COMMENT ON COLUMN "offers_offer_source"."name" IS 'Название источника';
COMMENT ON COLUMN "offers_offer_source"."slug" IS 'Slug источника';
COMMENT ON TABLE "offers_offer_source" IS 'Модель Источнк коммерческого предложения';
        CREATE TABLE IF NOT EXISTS "offers_offer" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "booking_amo_id" INT NOT NULL,
    "client_amo_id" INT NOT NULL,
    "offer_link" VARCHAR(250),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "uid" UUID,
    "source_id" INT REFERENCES "offers_offer_source" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "offers_offer"."booking_amo_id" IS 'ID сделки в АМО';
COMMENT ON COLUMN "offers_offer"."client_amo_id" IS 'ID клиента в АМО';
COMMENT ON COLUMN "offers_offer"."offer_link" IS 'Ссылка на КП в Тильда';
COMMENT ON COLUMN "offers_offer"."created_at" IS 'Дата и время создания';
COMMENT ON COLUMN "offers_offer"."updated_at" IS 'Дата и время создания';
COMMENT ON COLUMN "offers_offer"."uid" IS 'ID КП в АМО';
COMMENT ON COLUMN "offers_offer"."source_id" IS 'Источник КП';
COMMENT ON TABLE "offers_offer" IS 'Модель Коммерческого предложения';
        CREATE TABLE IF NOT EXISTS "offers_offer_property" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "property_glogal_id" VARCHAR(250) NOT NULL,
    "offer_id" INT NOT NULL REFERENCES "offers_offer" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "offers_offer_property"."property_glogal_id" IS 'Global ID объекта собственности';
COMMENT ON COLUMN "offers_offer_property"."offer_id" IS 'Коммерческое предложение';
COMMENT ON TABLE "offers_offer_property" IS 'Модель Объекты недвижимости для КП';
        CREATE TABLE IF NOT EXISTS "offers_template" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(250),
    "is_default" BOOL NOT NULL  DEFAULT False,
    "building_id" INT NOT NULL REFERENCES "buildings_building" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "offers_template"."name" IS 'Название шаблона';
COMMENT ON COLUMN "offers_template"."is_default" IS 'Шаблон по умолчанию?';
COMMENT ON COLUMN "offers_template"."building_id" IS 'Корпус';
COMMENT ON TABLE "offers_template" IS 'Модель Шаблоны КП';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "offers_offer" CASCADE;
        DROP TABLE IF EXISTS "offers_offer_property" CASCADE;
        DROP TABLE IF EXISTS "offers_offer_source" CASCADE;
        DROP TABLE IF EXISTS "offers_template" CASCADE;"""
