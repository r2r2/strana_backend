-- upgrade --
CREATE TABLE IF NOT EXISTS "notifications_notification" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "message" TEXT,
    "is_read" BOOL NOT NULL  DEFAULT False,
    "is_sent" BOOL NOT NULL  DEFAULT False,
    "sent" TIMESTAMPTZ,
    "read" TIMESTAMPTZ,
    "user_id" INT REFERENCES "users_user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "notifications_notification"."id" IS 'ID';
COMMENT ON COLUMN "notifications_notification"."message" IS 'Сообщение';
COMMENT ON COLUMN "notifications_notification"."is_read" IS 'Прочитано';
COMMENT ON COLUMN "notifications_notification"."is_sent" IS 'Отправлено';
COMMENT ON COLUMN "notifications_notification"."sent" IS 'Время отправление';
COMMENT ON COLUMN "notifications_notification"."read" IS 'Время просмотра';
COMMENT ON COLUMN "notifications_notification"."user_id" IS 'Пользователь';
COMMENT ON TABLE "notifications_notification" IS 'Уведомление';
-- downgrade --
DROP TABLE IF EXISTS "notifications_notification";
