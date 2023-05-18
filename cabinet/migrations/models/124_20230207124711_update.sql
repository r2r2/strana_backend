-- upgrade --
ALTER TABLE "users_notification_mute" ADD "times" INT NOT NULL  DEFAULT 0;
ALTER TABLE "users_notification_mute" ADD "blocked" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "users_notification_mute" ADD "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
-- downgrade --
ALTER TABLE "users_notification_mute" DROP COLUMN "times";
ALTER TABLE "users_notification_mute" DROP COLUMN "blocked";
ALTER TABLE "users_notification_mute" DROP COLUMN "created_at";
