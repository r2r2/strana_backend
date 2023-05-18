-- upgrade --
ALTER TABLE "projects_project" ADD "is_active" BOOL NOT NULL  DEFAULT True;
ALTER TABLE "projects_project" ADD "priority" INT;
-- downgrade --
ALTER TABLE "projects_project" DROP COLUMN "is_active";
ALTER TABLE "projects_project" DROP COLUMN "priority";
