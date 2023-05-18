-- upgrade --
CREATE TABLE IF NOT EXISTS "tips_tip" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "image" VARCHAR(500),
    "title" VARCHAR(200),
    "text" TEXT,
    "order" INT
);
COMMENT ON COLUMN "tips_tip"."id" IS 'ID';
COMMENT ON COLUMN "tips_tip"."image" IS 'Изображение';
COMMENT ON COLUMN "tips_tip"."title" IS 'Заголовок';
COMMENT ON COLUMN "tips_tip"."text" IS 'Текст';
COMMENT ON COLUMN "tips_tip"."order" IS 'Порядок';
COMMENT ON TABLE "tips_tip" IS 'Подсказка';
-- downgrade --
DROP TABLE IF EXISTS "tips_tip";
