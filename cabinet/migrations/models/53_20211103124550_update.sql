-- upgrade --
ALTER TABLE "booking_booking" ADD "mortgage_approved" BOOL;
ALTER TABLE "booking_booking" ADD "mortgage_was_approved_by_agent" BOOL;
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "mortgage_approved";
ALTER TABLE "booking_booking" DROP COLUMN "mortgage_was_approved_by_agent";
