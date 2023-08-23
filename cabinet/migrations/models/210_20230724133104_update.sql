-- upgrade --
ALTER TABLE "booking_booking" ADD "condition_chosen" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "condition_chosen";
