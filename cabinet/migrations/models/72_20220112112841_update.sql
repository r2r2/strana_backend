-- upgrade --
ALTER TABLE "buildings_building"
    DROP COLUMN "booking_price";
ALTER TABLE "buildings_building"
    DROP COLUMN "booking_period";
CREATE TABLE IF NOT EXISTS "buildings_building_booking_type"
(
    "id"     SERIAL NOT NULL PRIMARY KEY,
    "period" INT    NOT NULL,
    "price"  INT    NOT NULL
);
COMMENT ON COLUMN "buildings_building_booking_type"."id" IS 'ID';
COMMENT ON TABLE "buildings_building_booking_type" IS 'Тип бронирования у корпусов.';
CREATE TABLE "building_building_booking_type_m2m"
(
    "buildings_building_id"  INT NOT NULL REFERENCES "buildings_building" ("id") ON DELETE CASCADE,
    "buildingbookingtype_id" INT NOT NULL REFERENCES "buildings_building_booking_type" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "building_building_booking_type_m2m";
ALTER TABLE "buildings_building"
    ADD "booking_price" INT;
ALTER TABLE "buildings_building"
    ADD "booking_period" INT;
DROP TABLE IF EXISTS "buildings_building_booking_type";
