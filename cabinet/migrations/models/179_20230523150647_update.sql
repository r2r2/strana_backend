-- upgrade --
CREATE TABLE IF NOT EXISTS "text_block_text_block" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" TEXT,
    "text" TEXT,
    "slug" VARCHAR(100) NOT NULL UNIQUE,
    "lk_type" VARCHAR(10) NOT NULL,
    "description" TEXT
);
COMMENT ON COLUMN "text_block_text_block"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "text_block_text_block"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "text_block_text_block"."id" IS 'ID';
COMMENT ON COLUMN "text_block_text_block"."title" IS 'Заголовок блока';
COMMENT ON COLUMN "text_block_text_block"."text" IS 'Текст блока';
COMMENT ON COLUMN "text_block_text_block"."slug" IS 'Слаг текстового блока';
COMMENT ON COLUMN "text_block_text_block"."lk_type" IS 'Сервис ЛК, в котором применяется текстовый блок';
COMMENT ON COLUMN "text_block_text_block"."description" IS 'Описание назначения текстового блока';
COMMENT ON TABLE "text_block_text_block" IS 'Текстовый блок.';;
-- downgrade --
DROP TABLE IF EXISTS "text_block_text_block";
