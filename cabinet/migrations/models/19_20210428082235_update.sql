-- upgrade --
ALTER TABLE "booking_booking" ADD "email_force" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "booking_booking" ADD "email_sent" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "email_force";
ALTER TABLE "booking_booking" DROP COLUMN "email_sent";
