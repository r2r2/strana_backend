-- upgrade --
ALTER TABLE "buildings_building" ADD "total_floor" INT;
-- downgrade --
ALTER TABLE "buildings_building" DROP COLUMN "total_floor";
