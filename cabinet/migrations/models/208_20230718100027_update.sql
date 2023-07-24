-- upgrade --
CREATE TABLE IF NOT EXISTS "documents_instruction" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "slug" VARCHAR(50) NOT NULL,
    "link_text" TEXT NOT NULL,
    "file" VARCHAR(300)
);
COMMENT ON COLUMN "documents_instruction"."id" IS 'ID';
COMMENT ON COLUMN "documents_instruction"."slug" IS 'Слаг';
COMMENT ON COLUMN "documents_instruction"."link_text" IS 'Текст ссылки';
COMMENT ON COLUMN "documents_instruction"."file" IS 'Файл';
COMMENT ON TABLE "documents_instruction" IS 'Инструкция';;
-- downgrade --
DROP TABLE IF EXISTS "documents_instruction";
