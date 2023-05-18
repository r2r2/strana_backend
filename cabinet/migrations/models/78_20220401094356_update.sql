-- upgrade --
ALTER TABLE "booking_booking" ADD "scanned_passports_data" JSONB;
COMMENT ON COLUMN "booking_booking"."scanned_passports_data" IS 'Отсканированные данные паспортов';
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "scanned_passports_data";
