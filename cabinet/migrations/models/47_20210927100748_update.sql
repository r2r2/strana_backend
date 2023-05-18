-- upgrade --
ALTER TABLE "buildings_building" ADD "default_commission" DECIMAL(5,2);
-- downgrade --
ALTER TABLE "buildings_building" DROP COLUMN "default_commission";
