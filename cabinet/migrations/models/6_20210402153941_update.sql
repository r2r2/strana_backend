-- upgrade --
ALTER TABLE "properties_property" ADD "number" VARCHAR(100);
ALTER TABLE "properties_property" ADD "rooms" SMALLINT;
ALTER TABLE "booking_booking" ADD "floor_id" INT;
ALTER TABLE "booking_booking" ADD CONSTRAINT "fk_booking__floors_f_483f1d80" FOREIGN KEY ("floor_id") REFERENCES "floors_floor" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "booking_booking" DROP CONSTRAINT "fk_booking__floors_f_483f1d80";
ALTER TABLE "booking_booking" DROP COLUMN "floor_id";
ALTER TABLE "properties_property" DROP COLUMN "number";
ALTER TABLE "properties_property" DROP COLUMN "rooms";
