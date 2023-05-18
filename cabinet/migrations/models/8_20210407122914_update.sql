-- upgrade --
ALTER TABLE "booking_bookinglog" ADD "use_case" VARCHAR(200);
-- downgrade --
ALTER TABLE "booking_bookinglog" DROP COLUMN "use_case";
