from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "notifications_onboarding" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "message" TEXT NOT NULL,
    "slug" VARCHAR(50) NOT NULL,
    "button_text" VARCHAR(150) NOT NULL
);
COMMENT ON COLUMN "notifications_onboarding"."id" IS 'ID';
COMMENT ON COLUMN "notifications_onboarding"."message" IS 'Сообщение';
COMMENT ON COLUMN "notifications_onboarding"."slug" IS 'Слаг';
COMMENT ON COLUMN "notifications_onboarding"."button_text" IS 'Текс кнопки';
COMMENT ON TABLE "notifications_onboarding" IS 'Уведомления онбординга';
        CREATE TABLE IF NOT EXISTS "notifications_onboarding_user_through" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "is_read" BOOL NOT NULL  DEFAULT False,
    "is_sent" BOOL NOT NULL  DEFAULT False,
    "sent" TIMESTAMPTZ,
    "read" TIMESTAMPTZ,
    "onboarding_id" BIGINT NOT NULL REFERENCES "notifications_onboarding" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users_user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "notifications_onboarding_user_through"."is_read" IS 'Прочитано';
COMMENT ON COLUMN "notifications_onboarding_user_through"."is_sent" IS 'Отправлено';
COMMENT ON COLUMN "notifications_onboarding_user_through"."sent" IS 'Время отправления';
COMMENT ON COLUMN "notifications_onboarding_user_through"."read" IS 'Время просмотра';
COMMENT ON COLUMN "notifications_onboarding_user_through"."onboarding_id" IS 'Уведомления онбординга';
COMMENT ON COLUMN "notifications_onboarding_user_through"."user_id" IS 'Клиент';
COMMENT ON TABLE "notifications_onboarding_user_through" IS 'Уведомления онбординга конкретного пользователя';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "notifications_onboarding_user_through";
        DROP TABLE IF EXISTS "notifications_onboarding";"""
