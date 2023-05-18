-- upgrade --
ALTER TABLE "users_user" ADD "amocrm_id" BIGINT;
ALTER TABLE "projects_project" ADD "amocrm_enum" BIGINT;
ALTER TABLE "projects_project" ADD "amocrm_name" VARCHAR(200);
ALTER TABLE "projects_project" ADD "amocrm_organization" VARCHAR(200);
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "amocrm_id";
ALTER TABLE "projects_project" DROP COLUMN "amocrm_enum";
ALTER TABLE "projects_project" DROP COLUMN "amocrm_name";
ALTER TABLE "projects_project" DROP COLUMN "amocrm_organization";
