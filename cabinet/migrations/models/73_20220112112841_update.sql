-- upgrade --
ALTER TABLE "booking_booking" ADD COLUMN "booking_period" INT;
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "booking_period";
