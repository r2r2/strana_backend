-- upgrade --
ALTER TABLE "booking_booking" ADD "profitbase_booked" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "profitbase_booked";
