from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "news_news_settings" (
            "id" BIGSERIAL NOT NULL PRIMARY KEY,
            "default_image_preview" VARCHAR(500) NOT NULL,
            "default_image" VARCHAR(500) NOT NULL
        );
        COMMENT ON COLUMN "news_news_settings"."id" IS 'ID';
        COMMENT ON COLUMN "news_news_settings"."default_image_preview" IS 'Изображение (превью) по умолчанию';
        COMMENT ON COLUMN "news_news_settings"."default_image" IS 'Изображение по умолчанию';
        COMMENT ON TABLE "news_news_settings" IS 'Настройки новостей.';
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "news_news_settings";
        """
