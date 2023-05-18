-- upgrade --
CREATE TABLE IF NOT EXISTS "users_userlog" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "state_before" JSONB,
    "state_after" JSONB,
    "content" TEXT,
    "error_data" TEXT,
    "response_data" TEXT,
    "use_case" VARCHAR(200),
    "user_id" INT REFERENCES "users_user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "users_userlog"."id" IS 'ID';
COMMENT ON COLUMN "users_userlog"."created" IS 'Создано';
COMMENT ON COLUMN "users_userlog"."state_before" IS 'Состояние до';
COMMENT ON COLUMN "users_userlog"."state_after" IS 'Состояние после';
COMMENT ON COLUMN "users_userlog"."content" IS 'Контент';
COMMENT ON COLUMN "users_userlog"."error_data" IS 'Данные ошибки';
COMMENT ON COLUMN "users_userlog"."response_data" IS 'Данные ответа';
COMMENT ON COLUMN "users_userlog"."use_case" IS 'Сценарий';
COMMENT ON COLUMN "users_userlog"."user_id" IS 'Пользователь';
COMMENT ON TABLE "users_userlog" IS 'Лог пользователя';
-- downgrade --
DROP TABLE IF EXISTS "users_userlog";
