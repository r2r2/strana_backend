-- upgrade --
CREATE TABLE IF NOT EXISTS "additional_agreement_templates" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "template_name" VARCHAR(150) NOT NULL,
    "project_id" INT NOT NULL REFERENCES "projects_project" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "additional_agreement_templates"."id" IS 'ID';
COMMENT ON COLUMN "additional_agreement_templates"."template_name" IS 'Название шаблона';
COMMENT ON COLUMN "additional_agreement_templates"."project_id" IS 'ЖК';
COMMENT ON TABLE "additional_agreement_templates" IS 'Шаблоны дополнительных соглашений';
-- downgrade --
DROP TABLE IF EXISTS "additional_agreement_templates";
