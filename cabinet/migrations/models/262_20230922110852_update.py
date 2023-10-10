from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "additional_services_templates" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(150) NOT NULL,
    "description" TEXT NOT NULL,
    "button_text" TEXT NOT NULL,
    "slug" VARCHAR(50)  UNIQUE
);
COMMENT ON COLUMN "additional_services_templates"."id" IS 'ID';
COMMENT ON COLUMN "additional_services_templates"."title" IS 'Название';
COMMENT ON COLUMN "additional_services_templates"."description" IS 'Текст';
COMMENT ON COLUMN "additional_services_templates"."button_text" IS 'Текст кнопки';
COMMENT ON COLUMN "additional_services_templates"."slug" IS 'slug';
COMMENT ON TABLE "additional_services_templates" IS 'Шаблоны доп услуг';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "additional_services_templates";"""
