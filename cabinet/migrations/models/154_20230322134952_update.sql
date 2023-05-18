-- upgrade --
ALTER TABLE "agencies_additional_agreement" ADD "agency_id" INT;
ALTER TABLE "agencies_additional_agreement" ADD "booking_id" INT;
ALTER TABLE "agencies_additional_agreement" ADD "project_id" INT;
ALTER TABLE "agencies_additional_agreement" DROP COLUMN "agency_agreement_id";
ALTER TABLE "agencies_additional_agreement" DROP COLUMN "name";
ALTER TABLE "agencies_additional_agreement" ADD CONSTRAINT "fk_agencies_projects_6ec54ea3" FOREIGN KEY ("project_id") REFERENCES "projects_project" ("id") ON DELETE CASCADE;
ALTER TABLE "agencies_additional_agreement" ADD CONSTRAINT "fk_agencies_agencies_745832d7" FOREIGN KEY ("agency_id") REFERENCES "agencies_agency" ("id") ON DELETE CASCADE;
ALTER TABLE "agencies_additional_agreement" ADD CONSTRAINT "fk_agencies_booking__5e7753bb" FOREIGN KEY ("booking_id") REFERENCES "booking_booking" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "agencies_additional_agreement" DROP CONSTRAINT "fk_agencies_booking__5e7753bb";
ALTER TABLE "agencies_additional_agreement" DROP CONSTRAINT "fk_agencies_agencies_745832d7";
ALTER TABLE "agencies_additional_agreement" DROP CONSTRAINT "fk_agencies_projects_6ec54ea3";
ALTER TABLE "agencies_additional_agreement" ADD "agency_agreement_id" INT;
ALTER TABLE "agencies_additional_agreement" ADD "name" VARCHAR(100);
ALTER TABLE "agencies_additional_agreement" DROP COLUMN "agency_id";
ALTER TABLE "agencies_additional_agreement" DROP COLUMN "booking_id";
ALTER TABLE "agencies_additional_agreement" DROP COLUMN "project_id";
ALTER TABLE "agencies_additional_agreement" ADD CONSTRAINT "fk_agencies_agencies_39fcbc75" FOREIGN KEY ("agency_agreement_id") REFERENCES "agencies_agreement" ("id") ON DELETE CASCADE;
