-- upgrade --
ALTER TABLE "docs_templates" ADD "agreement_type_id" INT NOT NULL;
ALTER TABLE "docs_templates" DROP COLUMN "pipeline_id";
ALTER TABLE "docs_templates" DROP COLUMN "project_name";
ALTER TABLE "docs_templates" ALTER COLUMN "project_id" TYPE INT USING "project_id"::INT;
ALTER TABLE "agreement_type" ALTER COLUMN "description" DROP NOT NULL;
ALTER TABLE "docs_templates" ADD CONSTRAINT "fk_docs_tem_agreemen_1652ebf9" FOREIGN KEY ("agreement_type_id") REFERENCES "agreement_type" ("id") ON DELETE CASCADE;
ALTER TABLE "docs_templates" ADD CONSTRAINT "fk_docs_tem_projects_a5f25c6e" FOREIGN KEY ("project_id") REFERENCES "projects_project" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "docs_templates" DROP CONSTRAINT "fk_docs_tem_projects_a5f25c6e";
ALTER TABLE "docs_templates" DROP CONSTRAINT "fk_docs_tem_agreemen_1652ebf9";
ALTER TABLE "docs_templates" ADD "pipeline_id" INT;
ALTER TABLE "docs_templates" ADD "project_name" VARCHAR(150) NOT NULL;
ALTER TABLE "agreement_type" ALTER COLUMN "description" SET NOT NULL;
ALTER TABLE "docs_templates" DROP COLUMN "agreement_type_id";
ALTER TABLE "docs_templates" ALTER COLUMN "project_id" TYPE INT USING "project_id"::INT;
