-- upgrade --
ALTER TABLE "agencies_agency" DROP COLUMN "getdoc_lead_id";
ALTER TABLE "docs_templates" ADD "type" VARCHAR(50) NOT NULL;
ALTER TABLE "agencies_act" ALTER COLUMN "status_id" DROP NOT NULL;
ALTER TABLE "agencies_act" ALTER COLUMN "signed_at" DROP NOT NULL;
ALTER TABLE "agencies_act" ALTER COLUMN "number" DROP NOT NULL;
ALTER TABLE "agencies_agreement" ALTER COLUMN "status_id" DROP NOT NULL;
ALTER TABLE "agencies_agreement" ALTER COLUMN "signed_at" DROP NOT NULL;
ALTER TABLE "agencies_agreement" ALTER COLUMN "number" DROP NOT NULL;
ALTER TABLE "agreement_status" ALTER COLUMN "description" DROP NOT NULL;
CREATE UNIQUE INDEX "uid_agencies_ag_agency__414421" ON "agencies_agreement" ("agency_id", "template_name");
-- downgrade --
DROP INDEX "uid_agencies_ag_agency__414421";
ALTER TABLE "agencies_agency" ADD "getdoc_lead_id" BIGINT;
ALTER TABLE "agencies_act" ALTER COLUMN "status_id" SET NOT NULL;
ALTER TABLE "agencies_act" ALTER COLUMN "signed_at" SET NOT NULL;
ALTER TABLE "agencies_act" ALTER COLUMN "number" SET NOT NULL;
ALTER TABLE "docs_templates" DROP COLUMN "type";
ALTER TABLE "agencies_agreement" ALTER COLUMN "status_id" SET NOT NULL;
ALTER TABLE "agencies_agreement" ALTER COLUMN "signed_at" SET NOT NULL;
ALTER TABLE "agencies_agreement" ALTER COLUMN "number" SET NOT NULL;
ALTER TABLE "agreement_status" ALTER COLUMN "description" SET NOT NULL;
