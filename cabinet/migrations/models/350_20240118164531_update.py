from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "settings_feedback" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY
);
COMMENT ON COLUMN "settings_feedback"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "settings_feedback"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "settings_feedback"."id" IS 'ID';
COMMENT ON TABLE "settings_feedback" IS 'Настройки форм обратной связи';
        CREATE TABLE IF NOT EXISTS "privilege_feedback_email" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "full_name" VARCHAR(250) NOT NULL,
    "email" VARCHAR(250) NOT NULL,
    "feedback_settings_id" INT REFERENCES "settings_feedback" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "privilege_feedback_email"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "privilege_feedback_email"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "privilege_feedback_email"."id" IS 'ID';
COMMENT ON COLUMN "privilege_feedback_email"."full_name" IS 'ФИО';
COMMENT ON COLUMN "privilege_feedback_email"."email" IS 'Email';
COMMENT ON TABLE "privilege_feedback_email" IS 'Emails для результатов формы \"Программа привилегий\"';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "settings_feedback";
        DROP TABLE IF EXISTS "privilege_feedback_email";"""
