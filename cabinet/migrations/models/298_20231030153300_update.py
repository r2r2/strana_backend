from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    CREATE TABLE IF NOT EXISTS "notifications_template_content" (
        "id" SERIAL NOT NULL PRIMARY KEY,
        "description" TEXT NOT NULL,
        "slug" VARCHAR(50),
        "file" VARCHAR(300)
    );
    COMMENT ON COLUMN "notifications_template_content"."id" IS 'ID';
    COMMENT ON COLUMN "notifications_template_content"."description" IS 'Описание';
    COMMENT ON COLUMN "notifications_template_content"."slug" IS 'Слаг';
    COMMENT ON COLUMN "notifications_template_content"."file" IS 'Файл';
    COMMENT ON TABLE "notifications_template_content" IS 'Контент шаблонов писем';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "notifications_template_content";
        """
