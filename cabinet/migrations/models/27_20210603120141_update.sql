-- upgrade --
ALTER TABLE "agencies_agency" ADD "name" VARCHAR(100);
ALTER TABLE "agencies_agency" ALTER COLUMN "type" DROP NOT NULL;
-- downgrade --
ALTER TABLE "agencies_agency" DROP COLUMN "name";
ALTER TABLE "agencies_agency" ALTER COLUMN "type" SET NOT NULL;
