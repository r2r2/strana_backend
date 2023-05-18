-- upgrade --
ALTER TABLE "users_notification_mute" ADD "all_times" INT NOT NULL  DEFAULT 0;
ALTER TABLE "users_notification_mute" ADD "phone" VARCHAR(20);

UPDATE "users_notification_mute"
SET phone = users_user.phone, all_times = times
FROM "users_user"
WHERE users_notification_mute.user_id = users_user.id;

ALTER TABLE "users_notification_mute" DROP COLUMN "user_id";
ALTER TABLE "users_notification_mute" ALTER COLUMN "updated_at" TYPE TIMESTAMPTZ USING "updated_at"::TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "users_notification_mute" ADD "user_id" INT NOT NULL;
ALTER TABLE "users_notification_mute" DROP COLUMN "phone";
ALTER TABLE "users_notification_mute" DROP COLUMN "all_times";
ALTER TABLE "users_notification_mute" ALTER COLUMN "updated_at" TYPE TIMESTAMPTZ USING "updated_at"::TIMESTAMPTZ;
