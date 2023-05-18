-- upgrade --
ALTER TABLE "booking_booking" ADD "ddu_acceptance_datetime" TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "ddu_acceptance_datetime";
