-- upgrade --
ALTER TABLE "agencies_agency" ADD "is_imported" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "agencies_agency" DROP COLUMN "is_imported";
