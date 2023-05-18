-- upgrade --
ALTER TABLE "booking_booking" ADD "expires" TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "expires";
