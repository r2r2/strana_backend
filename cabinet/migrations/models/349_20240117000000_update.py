from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
CREATE TABLE IF NOT EXISTS "questionnaire_fields" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "slug" VARCHAR(255),
    "name" VARCHAR(255),
    "type" VARCHAR(255),
    "description" TEXT,
    "block_id" INT REFERENCES "questionnaire_documents_blocks" ("id") ON DELETE CASCADE,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "questionnaire_fields"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "questionnaire_fields"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "questionnaire_fields"."id" IS 'ID';
COMMENT ON COLUMN "questionnaire_fields"."slug" IS 'Слаг';
COMMENT ON COLUMN "questionnaire_fields"."name" IS 'Название';
COMMENT ON COLUMN "questionnaire_fields"."type" IS 'Тип';
COMMENT ON COLUMN "questionnaire_fields"."description" IS 'Описание';
COMMENT ON COLUMN "questionnaire_fields"."block_id" IS 'Блок';
COMMENT ON TABLE "questionnaire_fields" IS '12.11 Поля';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "questionnaire_fields";"""
