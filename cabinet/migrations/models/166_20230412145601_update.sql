-- upgrade --
ALTER TABLE "properties_property" ADD "total_floors" SMALLINT;
-- downgrade --
ALTER TABLE "properties_property" DROP COLUMN "total_floors";
