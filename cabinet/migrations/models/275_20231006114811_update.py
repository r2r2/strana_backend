from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "cities_dadata_settings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "api_key" TEXT NOT NULL,
    "secret_key" TEXT NOT NULL
);
COMMENT ON COLUMN "cities_dadata_settings"."api_key" IS 'API ключ';
COMMENT ON COLUMN "cities_dadata_settings"."secret_key" IS 'Секрет';
COMMENT ON TABLE "cities_dadata_settings" IS 'Модель настройки аторизации в DaData';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "cities_dadata_settings";"""
