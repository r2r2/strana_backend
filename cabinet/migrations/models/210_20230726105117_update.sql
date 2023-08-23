-- upgrade --
ALTER TABLE "buildings_building_booking_type" ADD "priority" INT;
-- downgrade --
ALTER TABLE "buildings_building_booking_type" DROP COLUMN "priority";
