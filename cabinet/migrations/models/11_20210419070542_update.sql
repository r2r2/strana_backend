-- upgrade --
ALTER TABLE "booking_bookinglog" ADD "error_data" TEXT;
-- downgrade --
ALTER TABLE "booking_bookinglog" DROP COLUMN "error_data";
