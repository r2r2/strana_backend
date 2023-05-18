-- upgrade --
ALTER TABLE "booking_booking" ADD "host" VARCHAR(100);
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "host";
