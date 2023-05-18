-- upgrade --
ALTER TABLE "users_notification_mute" ADD "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE "users_notification_mute" ALTER COLUMN "created_at" TYPE TIMESTAMPTZ USING "created_at"::TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "users_notification_mute" DROP COLUMN "updated_at";
ALTER TABLE "users_notification_mute" ALTER COLUMN "created_at" TYPE TIMESTAMPTZ USING "created_at"::TIMESTAMPTZ;
