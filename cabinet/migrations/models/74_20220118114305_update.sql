-- upgrade --
CREATE TABLE IF NOT EXISTS "users_notification_mute" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "user_id" INT NOT NULL REFERENCES "users_user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "users_notification_mute"."user_id" IS 'Пользователь';
COMMENT ON TABLE "users_notification_mute" IS 'Запреты на отправку оповещений пользователям';;
-- downgrade --
DROP TABLE IF EXISTS "users_notification_mute";
