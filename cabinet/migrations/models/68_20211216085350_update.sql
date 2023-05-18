-- upgrade --
ALTER TABLE "booking_ddu" ADD COLUMN "create_datetime" TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "booking_ddu" DROP COLUMN "create_datetime";
