-- upgrade --
ALTER TABLE "agencies_agency" ADD "files" JSONB;
-- downgrade --
ALTER TABLE "agencies_agency" DROP COLUMN "files";
