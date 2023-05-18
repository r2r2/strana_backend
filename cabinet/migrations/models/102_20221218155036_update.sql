-- upgrade --
CREATE TABLE IF NOT EXISTS "cities_city" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(150) NOT NULL,
    "slug" VARCHAR(100) NOT NULL
);
COMMENT ON TABLE "cities_city" IS 'Модель Города';;
CREATE TABLE IF NOT EXISTS "amocrm_pipelines" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(150) NOT NULL
);
COMMENT ON TABLE "amocrm_pipelines" IS 'Модель Воронки';;
CREATE TABLE IF NOT EXISTS "amocrm_statuses" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(150) NOT NULL,
    "pipeline_id" INT NOT NULL REFERENCES "amocrm_pipelines" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "amocrm_statuses" IS 'Модель Статуса';
-- downgrade --
DROP TABLE IF EXISTS "cities_city";
DROP TABLE IF EXISTS "amocrm_pipelines";
DROP TABLE IF EXISTS "amocrm_statuses";
