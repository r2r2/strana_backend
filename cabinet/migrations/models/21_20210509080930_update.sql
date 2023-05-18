-- upgrade --
ALTER TABLE "buildings_building" ADD "address" VARCHAR(300);
-- downgrade --
ALTER TABLE "buildings_building" DROP COLUMN "address";
