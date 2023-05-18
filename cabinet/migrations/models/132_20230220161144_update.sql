-- upgrade --
ALTER TABLE "users_notification_mute" DROP COLUMN "all_times";
ALTER TABLE "users_notification_mute" ALTER COLUMN "updated_at" TYPE TIMESTAMPTZ USING "updated_at"::TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "users_notification_mute" ADD "all_times" INT NOT NULL  DEFAULT 0;
ALTER TABLE "users_notification_mute" ALTER COLUMN "updated_at" TYPE TIMESTAMPTZ USING "updated_at"::TIMESTAMPTZ;
