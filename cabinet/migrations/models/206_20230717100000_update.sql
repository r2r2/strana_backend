-- upgrade --
ALTER TABLE "projects_project" ADD COLUMN IF NOT EXISTS "flats_reserv_time" DOUBLE PRECISION;
ALTER TABLE "buildings_building" ADD COLUMN IF NOT EXISTS "flats_reserv_time" DOUBLE PRECISION;
CREATE TABLE IF NOT EXISTS "settings_booking_settings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255),
    "default_flats_reserv_time" DOUBLE PRECISION   DEFAULT 24,
    "created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "updated_at" TIMESTAMP WITH TIME ZONE NOT NULL
);
COMMENT ON COLUMN "settings_booking_settings"."id" IS 'ID';
COMMENT ON COLUMN "settings_booking_settings"."name" IS 'Название';
COMMENT ON COLUMN "settings_booking_settings"."default_flats_reserv_time" IS 'Время резервирования квартир по умолчанию (ч)';
COMMENT ON TABLE "settings_booking_settings" IS 'Настройки бронирования';
-- downgrade --
ALTER TABLE "projects_project" DROP COLUMN "flats_reserv_time";
ALTER TABLE "buildings_building" DROP COLUMN "flats_reserv_time";
DROP TABLE IF EXISTS "settings_booking_settings";
