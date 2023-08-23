-- upgrade --
ALTER TABLE "settings_booking_settings" ALTER COLUMN "lifetime" TYPE DOUBLE PRECISION USING "lifetime"::DOUBLE PRECISION;
ALTER TABLE "settings_booking_settings" ALTER COLUMN "updated_lifetime" TYPE DOUBLE PRECISION USING "updated_lifetime"::DOUBLE PRECISION;
ALTER TABLE "settings_booking_settings" ALTER COLUMN "extension_deadline" TYPE DOUBLE PRECISION USING "extension_deadline"::DOUBLE PRECISION;
-- downgrade --
ALTER TABLE "settings_booking_settings" ALTER COLUMN "lifetime" TYPE INT USING "lifetime"::INT;
ALTER TABLE "settings_booking_settings" ALTER COLUMN "updated_lifetime" TYPE INT USING "updated_lifetime"::INT;
ALTER TABLE "settings_booking_settings" ALTER COLUMN "extension_deadline" TYPE INT USING "extension_deadline"::INT;
