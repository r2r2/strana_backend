-- upgrade --
ALTER TABLE "buildings_building_booking_type" ADD "amocrm_id" BIGINT;
-- downgrade --
ALTER TABLE "buildings_building_booking_type" DROP COLUMN "amocrm_id";
