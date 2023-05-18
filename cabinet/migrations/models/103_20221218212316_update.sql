-- upgrade --
CREATE TABLE IF NOT EXISTS "users_checks_terms" (
    "uid" UUID NOT NULL  PRIMARY KEY,
    "is_agent" VARCHAR(8) NOT NULL,
    "more_days" INT,
    "less_days" INT,
    "priority" INT NOT NULL,
    "unique_value" VARCHAR(28) NOT NULL
);
COMMENT ON COLUMN "users_checks_terms"."uid" IS 'ID';
COMMENT ON COLUMN "users_checks_terms"."is_agent" IS 'Есть агент';
COMMENT ON COLUMN "users_checks_terms"."more_days" IS 'Больше скольки дней сделка находится в статусе';
COMMENT ON COLUMN "users_checks_terms"."less_days" IS 'Меньше скольки дней сделка находится в статусе';
COMMENT ON COLUMN "users_checks_terms"."priority" IS 'Приоритет';
COMMENT ON COLUMN "users_checks_terms"."unique_value" IS 'Статус уникальности';
COMMENT ON TABLE "users_checks_terms" IS 'Условия проверки на уникальность';;
CREATE TABLE IF NOT EXISTS "users_checks_terms_cities" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "city_id" INT NOT NULL REFERENCES "cities_city" ("id") ON DELETE CASCADE,
    "term_id" UUID NOT NULL REFERENCES "users_checks_terms" ("uid") ON DELETE CASCADE,
    CONSTRAINT "uid_users_check_city_id_cd7e2d" UNIQUE ("city_id", "term_id")
);;
CREATE TABLE IF NOT EXISTS "users_checks_terms_pipelines" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "pipeline_id" INT NOT NULL REFERENCES "amocrm_pipelines" ("id") ON DELETE CASCADE,
    "term_id" UUID NOT NULL REFERENCES "users_checks_terms" ("uid") ON DELETE CASCADE,
    CONSTRAINT "uid_users_check_pipelin_c761e5" UNIQUE ("pipeline_id", "term_id")
);;
CREATE TABLE IF NOT EXISTS "users_checks_terms_statuses" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "status_id" INT NOT NULL REFERENCES "amocrm_statuses" ("id") ON DELETE CASCADE,
    "term_id" UUID NOT NULL REFERENCES "users_checks_terms" ("uid") ON DELETE CASCADE,
    CONSTRAINT "uid_users_check_status__ca0209" UNIQUE ("status_id", "term_id")
);;
-- downgrade --
DROP TABLE IF EXISTS "users_checks_terms_pipelines";
DROP TABLE IF EXISTS "users_checks_terms_statuses";
DROP TABLE IF EXISTS "users_checks_terms_cities";
DROP TABLE IF EXISTS "users_checks_terms";
