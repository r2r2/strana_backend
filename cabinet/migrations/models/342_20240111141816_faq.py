from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "faq_faq" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "slug" VARCHAR(100) NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "order" INT NOT NULL  DEFAULT 0,
    "question" VARCHAR(100) NOT NULL,
    "answer" TEXT NOT NULL
);
COMMENT ON COLUMN "faq_faq"."id" IS 'ID';
COMMENT ON COLUMN "faq_faq"."slug" IS 'Слаг';
COMMENT ON COLUMN "faq_faq"."is_active" IS 'Активный';
COMMENT ON COLUMN "faq_faq"."order" IS 'Порядок';
COMMENT ON COLUMN "faq_faq"."question" IS 'Вопрос';
COMMENT ON COLUMN "faq_faq"."answer" IS 'Ответ';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "faq_faq";"""
