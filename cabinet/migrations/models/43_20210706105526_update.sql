-- upgrade --
ALTER TABLE "agencies_agency" ADD "is_deleted" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "agencies_agency" DROP COLUMN "is_deleted";
