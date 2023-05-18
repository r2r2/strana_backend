-- upgrade --
ALTER TABLE "agencies_act" ADD "project_id" INT;
ALTER TABLE "agencies_act" ADD CONSTRAINT "fk_agencies_projects_5b0cc4a8" FOREIGN KEY ("project_id") REFERENCES "projects_project" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "agencies_act" DROP CONSTRAINT "fk_agencies_projects_5b0cc4a8";
ALTER TABLE "agencies_act" DROP COLUMN "project_id";
