-- upgrade --
ALTER TABLE "projects_project" ADD "amo_responsible_user_id" VARCHAR(200);
ALTER TABLE "projects_project" ADD "amo_pipeline_id" VARCHAR(200);
ALTER TABLE "booking_booking" ADD "tags" JSONB;
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "tags";
ALTER TABLE "projects_project" DROP COLUMN "amo_responsible_user_id";
ALTER TABLE "projects_project" DROP COLUMN "amo_pipeline_id";
