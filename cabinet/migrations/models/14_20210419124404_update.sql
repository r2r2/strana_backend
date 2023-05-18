-- upgrade --
ALTER TABLE "booking_booking" ADD "origin" VARCHAR(100);
ALTER TABLE "booking_booking" DROP COLUMN "host";
-- downgrade --
ALTER TABLE "booking_booking" ADD "host" VARCHAR(100);
ALTER TABLE "booking_booking" DROP COLUMN "origin";
