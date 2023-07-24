-- upgrade --
CREATE TABLE IF NOT EXISTS "agencies_additional_agreement_creating_data" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "reason_comment" VARCHAR(300),
    "additionals_created" BOOL NOT NULL  DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "agencies_additional_agreement_creating_data"."id" IS 'ID';
COMMENT ON COLUMN "agencies_additional_agreement_creating_data"."reason_comment" IS 'Комментарий (администратора)';
COMMENT ON COLUMN "agencies_additional_agreement_creating_data"."additionals_created" IS 'ДС сгенерированы';
CREATE TABLE "additional_data_projects" (
    "project_id" INT NOT NULL REFERENCES "projects_project" ("id") ON DELETE CASCADE,
    "additional_data_id" INT NOT NULL REFERENCES "agencies_additional_agreement_creating_data" ("id") ON DELETE CASCADE
);
CREATE TABLE "additional_data_agencies" (
    "agency_id" INT NOT NULL REFERENCES "agencies_agency" ("id") ON DELETE CASCADE,
    "additional_data_id" INT NOT NULL REFERENCES "agencies_additional_agreement_creating_data" ("id") ON DELETE CASCADE
);
ALTER TABLE "agencies_additional_agreement" ADD "creating_data_id" INT;
ALTER TABLE "agencies_additional_agreement" ADD CONSTRAINT "fk_agencies_agencies_2f391388" FOREIGN KEY ("creating_data_id") REFERENCES "agencies_additional_agreement_creating_data" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "agencies_additional_agreement" DROP CONSTRAINT "fk_agencies_agencies_2f391388";
DROP TABLE IF EXISTS "additional_data_agencies";
DROP TABLE IF EXISTS "additional_data_projects";
DROP TABLE IF EXISTS "agencies_additional_agreement_creating_data";
ALTER TABLE "agencies_additional_agreement" DROP COLUMN "creating_data_id";
