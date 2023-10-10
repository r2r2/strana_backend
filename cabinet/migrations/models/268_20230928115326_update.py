from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "settings_add_service_settings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(100)
);
COMMENT ON COLUMN "settings_add_service_settings"."id" IS 'ID';
COMMENT ON COLUMN "settings_add_service_settings"."email" IS 'Email';
COMMENT ON TABLE "settings_add_service_settings" IS 'Настройки доп. услуг';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "settings_add_service_settings";"""
