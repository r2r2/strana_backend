-- upgrade --
CREATE TABLE IF NOT EXISTS "docs_templates" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "project_id" INT NOT NULL,
    "project_name" VARCHAR(150) NOT NULL,
    "template_name" VARCHAR(150) NOT NULL,
    "pipeline_id" INT REFERENCES "amocrm_pipelines" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "docs_templates"."id" IS 'ID';
COMMENT ON COLUMN "docs_templates"."project_id" IS 'ID проекта';
COMMENT ON COLUMN "docs_templates"."project_name" IS 'Название проекта';
COMMENT ON COLUMN "docs_templates"."template_name" IS 'Название шаблона';
COMMENT ON COLUMN "docs_templates"."pipeline_id" IS 'Воронка проекта';
COMMENT ON TABLE "docs_templates" IS 'Репозиторий шаблонов договоров';
-- downgrade --
DROP TABLE IF EXISTS "docs_templates";
