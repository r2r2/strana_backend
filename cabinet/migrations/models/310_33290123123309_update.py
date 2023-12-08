from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "slider_auth" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "priority" INT NOT NULL  DEFAULT 0,
    "title" VARCHAR(300),
    "subtitle" VARCHAR(300),
    "desktop_media" VARCHAR(300),
    "tablet_media" VARCHAR(300),
    "mobile_media" VARCHAR(300)
);
COMMENT ON COLUMN "slider_auth"."is_active" IS 'Активность';
COMMENT ON COLUMN "slider_auth"."priority" IS 'Приоритет';
COMMENT ON COLUMN "slider_auth"."title" IS 'Заголовок слайда';
COMMENT ON COLUMN "slider_auth"."subtitle" IS 'Подзаголовок слайда';
COMMENT ON COLUMN "slider_auth"."desktop_media" IS 'Картинка/видео для десктопа';
COMMENT ON COLUMN "slider_auth"."tablet_media" IS 'Картинка/видео для планшета';
COMMENT ON COLUMN "slider_auth"."mobile_media" IS 'Картинка/видео для мобильной версии';
COMMENT ON TABLE "slider_auth" IS 'Модель слайдера авторизации';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "slider_auth";"""
