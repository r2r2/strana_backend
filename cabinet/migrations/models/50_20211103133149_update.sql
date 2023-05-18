-- upgrade --
ALTER TABLE "booking_booking" ADD "bill_paid" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "bill_paid";
