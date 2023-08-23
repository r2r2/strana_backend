-- upgrade --
ALTER TABLE "settings_booking_settings" ADD "updated_lifetime" INT;
UPDATE settings_booking_settings
SET lifetime = 30,
    updated_lifetime = 25,
    extension_deadline = 5,
    max_extension_number = 3;
-- downgrade --
ALTER TABLE "settings_booking_settings" DROP COLUMN "updated_lifetime";
