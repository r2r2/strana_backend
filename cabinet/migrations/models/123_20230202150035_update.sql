-- upgrade --
ALTER TABLE "projects_project" ADD "status" VARCHAR(11) NOT NULL  DEFAULT 'Текущий';
-- downgrade --
ALTER TABLE "projects_project" DROP COLUMN "status";
