-- upgrade --
ALTER TABLE "agencies_agency" ADD "getdoc_lead_id" BIGINT;
-- downgrade --
ALTER TABLE "agencies_agency" DROP COLUMN "getdoc_lead_id";
