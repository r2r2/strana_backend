-- upgrade --
ALTER TABLE "properties_property" ADD "status" SMALLINT;
-- downgrade --
ALTER TABLE "properties_property" DROP COLUMN "status";
