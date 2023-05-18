-- upgrade --
ALTER TABLE "buildings_building" ADD "booking_price" INT;
ALTER TABLE "buildings_building" ADD "booking_period" INT;
-- downgrade --
ALTER TABLE "buildings_building" DROP COLUMN "booking_price";
ALTER TABLE "buildings_building" DROP COLUMN "booking_period";
