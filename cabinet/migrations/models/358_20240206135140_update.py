from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "documents_document_archive" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "offer_text" TEXT NOT NULL,
    "slug" VARCHAR(50) NOT NULL,
    "file" VARCHAR(300),
    "date_time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "documents_document_archive"."id" IS 'ID';
COMMENT ON COLUMN "documents_document_archive"."offer_text" IS 'Текст';
COMMENT ON COLUMN "documents_document_archive"."slug" IS 'Слаг';
COMMENT ON COLUMN "documents_document_archive"."file" IS 'Файл';
COMMENT ON COLUMN "documents_document_archive"."date_time" IS 'Дата, время создания';
COMMENT ON TABLE "documents_document_archive" IS 'Архив документов (шаблонов оферт)';

INSERT INTO "documents_document_archive" (offer_text, slug, file)
SELECT text, slug, file 
FROM documents_document;
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "documents_document_archive";
        """
