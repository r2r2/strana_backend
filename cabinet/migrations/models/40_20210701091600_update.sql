-- upgrade --
ALTER TABLE "agencies_agency" DROP COLUMN "files";
-- downgrade --
ALTER TABLE "agencies_agency" ADD "files" JSONB;
