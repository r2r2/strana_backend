-- upgrade --
CREATE TABLE IF NOT EXISTS "documents_escrow" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "slug" VARCHAR(50) NOT NULL,
    "file" VARCHAR(300)
);
COMMENT ON COLUMN "documents_escrow"."id" IS 'ID';
COMMENT ON COLUMN "documents_escrow"."slug" IS 'Слаг';
COMMENT ON COLUMN "documents_escrow"."file" IS 'Файл';
COMMENT ON TABLE "documents_escrow" IS 'Памятка эскроу';
-- downgrade --
DROP TABLE IF EXISTS "documents_escrow";
