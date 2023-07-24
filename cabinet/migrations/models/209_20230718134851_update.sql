-- upgrade --
ALTER TABLE "projects_project" ADD "discount" SMALLINT NOT NULL  DEFAULT 0;
ALTER TABLE "buildings_building" ADD "discount" SMALLINT NOT NULL  DEFAULT 0;
-- downgrade --
ALTER TABLE "projects_project" DROP COLUMN "discount";
ALTER TABLE "buildings_building" DROP COLUMN "discount";
