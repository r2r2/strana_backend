-- upgrade --
DROP INDEX "uid_agencies_ag_agency__414421";
-- downgrade --
CREATE UNIQUE INDEX "uid_agencies_ag_agency__414421" ON "agencies_agreement" ("agency_id", "template_name");
