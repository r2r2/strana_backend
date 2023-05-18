-- upgrade --
CREATE TABLE IF NOT EXISTS "users_managers" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "lastname" VARCHAR(100) NOT NULL,
    "patronymic" VARCHAR(100),
    "position" VARCHAR(512),
    "phone" VARCHAR(20),
    "work_schedule" VARCHAR(512),
    "photo" VARCHAR(2000),
    "city" VARCHAR(50) NOT NULL  DEFAULT 'toymen'
);
CREATE INDEX IF NOT EXISTS "idx_users_manag_city_afd9c4" ON "users_managers" ("city");
COMMENT ON COLUMN "users_managers"."id" IS 'ID';
COMMENT ON COLUMN "users_managers"."name" IS 'Имя';
COMMENT ON COLUMN "users_managers"."lastname" IS 'Фамилия';
COMMENT ON COLUMN "users_managers"."patronymic" IS 'Отчество';
COMMENT ON COLUMN "users_managers"."position" IS 'Должность';
COMMENT ON COLUMN "users_managers"."phone" IS 'Телефон';
COMMENT ON COLUMN "users_managers"."work_schedule" IS 'Расписание работы';
COMMENT ON COLUMN "users_managers"."photo" IS 'Фотография';
COMMENT ON COLUMN "users_managers"."city" IS 'Город менеджера';
COMMENT ON TABLE "users_managers" IS 'Менеджеры \"Страны\"';
-- downgrade --
DROP TABLE IF EXISTS "users_managers";
