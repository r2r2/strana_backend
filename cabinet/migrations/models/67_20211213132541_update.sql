-- upgrade --
ALTER TABLE "booking_booking" ADD "deleted_in_amo" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "deleted_in_amo";
