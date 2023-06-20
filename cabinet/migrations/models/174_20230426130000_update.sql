-- upgrade --
CREATE TABLE IF NOT EXISTS "users_pinning_status" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "priority" INT NOT NULL,
    "result" VARCHAR(36) NOT NULL
);
COMMENT ON COLUMN "users_pinning_status"."id" IS 'ID';
COMMENT ON COLUMN "users_pinning_status"."priority" IS 'Приоритет';
COMMENT ON COLUMN "users_pinning_status"."result" IS 'Статус закрепления';
COMMENT ON TABLE "users_pinning_status" IS 'Модель статусов закрепления';;
CREATE TABLE IF NOT EXISTS "users_pinning_status_cities" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "city_id" INT NOT NULL REFERENCES "cities_city" ("id") ON DELETE CASCADE,
    "pinning_id" INT NOT NULL REFERENCES "users_pinning_status" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_users_pinni_city_id_1476b0" UNIQUE ("city_id", "pinning_id")
);
COMMENT ON COLUMN "users_pinning_status_cities"."id" IS 'ID';
COMMENT ON TABLE "users_pinning_status_cities" IS 'Модель городов - статусов закрепления';;
CREATE TABLE IF NOT EXISTS "users_pinning_status_pipelines" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "pinning_id" INT NOT NULL REFERENCES "users_pinning_status" ("id") ON DELETE CASCADE,
    "pipeline_id" INT NOT NULL REFERENCES "amocrm_pipelines" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_users_pinni_pipelin_83f188" UNIQUE ("pipeline_id", "pinning_id")
);
COMMENT ON COLUMN "users_pinning_status_pipelines"."id" IS 'ID';
COMMENT ON TABLE "users_pinning_status_pipelines" IS 'Модель воронок - статусов закрепления';;
CREATE TABLE IF NOT EXISTS "users_pinning_status_statuses" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "pinning_id" INT NOT NULL REFERENCES "users_pinning_status" ("id") ON DELETE CASCADE,
    "status_id" INT NOT NULL REFERENCES "amocrm_statuses" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_users_pinni_status__0da0bb" UNIQUE ("status_id", "pinning_id")
);
COMMENT ON COLUMN "users_pinning_status_statuses"."id" IS 'ID';
COMMENT ON TABLE "users_pinning_status_statuses" IS 'Модель статусов - статусов закрепления';;
CREATE TABLE IF NOT EXISTS "users_user_pinning_status" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "status" VARCHAR(20) NOT NULL  DEFAULT 'unknown',
    "user_id" INT NOT NULL REFERENCES "users_user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_users_user__user_id_af372e" ON "users_user_pinning_status" ("user_id");
COMMENT ON COLUMN "users_user_pinning_status"."id" IS 'ID';
COMMENT ON COLUMN "users_user_pinning_status"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "users_user_pinning_status"."status" IS 'Статус';
COMMENT ON COLUMN "users_user_pinning_status"."user_id" IS 'Пользователь';
COMMENT ON TABLE "users_user_pinning_status" IS 'Статус закрепления пользователя';;
-- downgrade --
DROP TABLE IF EXISTS "users_pinning_status_pipelines";
DROP TABLE IF EXISTS "users_pinning_status_cities";
DROP TABLE IF EXISTS "users_pinning_status";
DROP TABLE IF EXISTS "users_pinning_status_statuses";
DROP TABLE IF EXISTS "users_user_pinning_status";
