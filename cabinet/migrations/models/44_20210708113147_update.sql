-- upgrade --
ALTER TABLE "documents_document" ADD "file" VARCHAR(300);
-- downgrade --
ALTER TABLE "documents_document" DROP COLUMN "file";
