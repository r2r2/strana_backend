-- upgrade --
ALTER TABLE "settings_booking_settings" ADD "max_extension_number" INT;
ALTER TABLE "settings_booking_settings" ADD "extension_deadline" INT;
ALTER TABLE "settings_booking_settings" ADD "lifetime" INT;
ALTER TABLE "booking_booking" ADD "extension_number" INT;
ALTER TABLE "booking_booking" ADD "fixation_expires" TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "settings_booking_settings" DROP COLUMN "max_extension_number";
ALTER TABLE "settings_booking_settings" DROP COLUMN "extension_deadline";
ALTER TABLE "settings_booking_settings" DROP COLUMN "lifetime";
ALTER TABLE "booking_booking" DROP COLUMN "extension_number";
ALTER TABLE "booking_booking" DROP COLUMN "fixation_expires";
