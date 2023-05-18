-- upgrade --
ALTER TABLE "users_checks" ALTER COLUMN "agency_id" TYPE INT USING "agency_id"::INT;
ALTER TABLE "users_user" ADD "is_deleted" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "users_user" ALTER COLUMN "agency_id" TYPE INT USING "agency_id"::INT;
ALTER TABLE "users_user" ALTER COLUMN "maintained_id" TYPE INT USING "maintained_id"::INT;
ALTER TABLE "booking_booking" ALTER COLUMN "agency_id" TYPE INT USING "agency_id"::INT;
ALTER TABLE "notifications_notification" ALTER COLUMN "agency_id" TYPE INT USING "agency_id"::INT;
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "is_deleted";
ALTER TABLE "users_user" ALTER COLUMN "agency_id" TYPE INT USING "agency_id"::INT;
ALTER TABLE "users_user" ALTER COLUMN "maintained_id" TYPE INT USING "maintained_id"::INT;
ALTER TABLE "users_checks" ALTER COLUMN "agency_id" TYPE INT USING "agency_id"::INT;
ALTER TABLE "booking_booking" ALTER COLUMN "agency_id" TYPE INT USING "agency_id"::INT;
ALTER TABLE "notifications_notification" ALTER COLUMN "agency_id" TYPE INT USING "agency_id"::INT;
