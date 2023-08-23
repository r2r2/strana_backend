-- upgrade --
ALTER TABLE "task_management_taskfields" ADD "field_name" VARCHAR(100) NOT NULL DEFAULT '';
-- downgrade --
ALTER TABLE "task_management_taskfields" DROP COLUMN "field_name";
