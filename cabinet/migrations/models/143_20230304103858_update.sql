-- upgrade --
ALTER TABLE "users_userlog" ADD "state_difference" JSONB;
ALTER TABLE "booking_bookinglog" ADD "state_difference" JSONB;
ALTER TABLE "agencies_agencylog" ADD "state_difference" JSONB;
-- downgrade --
ALTER TABLE "users_userlog" DROP COLUMN "state_difference";
ALTER TABLE "agencies_agencylog" DROP COLUMN "state_difference";
ALTER TABLE "booking_bookinglog" DROP COLUMN "state_difference";
