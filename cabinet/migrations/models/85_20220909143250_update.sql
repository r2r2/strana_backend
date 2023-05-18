-- upgrade --
ALTER TABLE "users_checks" ALTER COLUMN "comment" TYPE VARCHAR(2000) USING "comment"::VARCHAR(2000);
ALTER TABLE "booking_booking" ADD "created_source" VARCHAR(100);
-- downgrade --
ALTER TABLE "users_checks" ALTER COLUMN "comment" TYPE VARCHAR(1000) USING "comment"::VARCHAR(1000);
ALTER TABLE "booking_booking" DROP COLUMN "created_source";
