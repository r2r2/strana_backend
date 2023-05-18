-- upgrade --
ALTER TABLE "booking_booking" DROP COLUMN "client_needs_help_with_mortgage";
-- downgrade --
ALTER TABLE "booking_booking" ADD "client_needs_help_with_mortgage" BOOL;
