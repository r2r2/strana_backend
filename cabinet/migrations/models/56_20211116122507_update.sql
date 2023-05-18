-- upgrade --
ALTER TABLE "booking_booking" ADD "signing_date" DATE;
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "signing_date";
