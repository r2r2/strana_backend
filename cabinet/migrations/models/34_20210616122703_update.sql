-- upgrade --
ALTER TABLE "users_checks" ADD "agency_id" INT;
ALTER TABLE "notifications_notification" ALTER COLUMN "sent" TYPE TIMESTAMPTZ USING "sent"::TIMESTAMPTZ;
ALTER TABLE "users_checks" ADD CONSTRAINT "fk_users_ch_agencies_29682829" FOREIGN KEY ("agency_id") REFERENCES "agencies_agency" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "users_checks" DROP CONSTRAINT "fk_users_ch_agencies_29682829";
ALTER TABLE "users_checks" DROP COLUMN "agency_id";
ALTER TABLE "notifications_notification" ALTER COLUMN "sent" TYPE TIMESTAMPTZ USING "sent"::TIMESTAMPTZ;
