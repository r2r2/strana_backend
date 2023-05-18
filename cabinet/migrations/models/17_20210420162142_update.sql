-- upgrade --
ALTER TABLE "projects_project" ADD "slug" VARCHAR(100);
-- downgrade --
ALTER TABLE "projects_project" DROP COLUMN "slug";
