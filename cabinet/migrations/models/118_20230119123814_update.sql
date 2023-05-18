-- upgrade --
ALTER TABLE "amocrm_pipelines" ALTER COLUMN "name" TYPE VARCHAR(150) USING "name"::VARCHAR(150);
ALTER TABLE "amocrm_pipelines" ALTER COLUMN "is_main" TYPE BOOL USING "is_main"::BOOL;
CREATE TABLE IF NOT EXISTS "acts_templates" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "template_name" VARCHAR(150) NOT NULL,
    "project_id" INT NOT NULL REFERENCES "projects_project" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "acts_templates"."id" IS 'ID';
COMMENT ON COLUMN "acts_templates"."template_name" IS 'Название шаблона';
COMMENT ON COLUMN "acts_templates"."project_id" IS 'Проект';
COMMENT ON TABLE "acts_templates" IS 'Репозиторий шаблонов актов';
-- downgrade --
ALTER TABLE "amocrm_pipelines" ALTER COLUMN "name" TYPE VARCHAR(150) USING "name"::VARCHAR(150);
ALTER TABLE "amocrm_pipelines" ALTER COLUMN "is_main" TYPE BOOL USING "is_main"::BOOL;
DROP TABLE IF EXISTS "acts_templates";
