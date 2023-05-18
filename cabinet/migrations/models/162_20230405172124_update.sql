-- upgrade --
ALTER TABLE "task_management_button" ALTER COLUMN "style" TYPE VARCHAR(20) USING "style"::VARCHAR(20);
ALTER TABLE "task_management_button" ALTER COLUMN "status_id" TYPE INT USING "status_id"::INT;
ALTER TABLE "task_management_taskchain" DROP COLUMN IF EXISTS "task_visibility";
ALTER TABLE "task_management_taskchain" DROP COLUMN IF EXISTS "booking_substage";
ALTER TABLE "task_management_taskinstance" ADD IF NOT EXISTS "sensei_pid" INT;
ALTER TABLE "task_management_taskinstance" ALTER COLUMN "comment" DROP NOT NULL;
ALTER TABLE "task_management_button" ADD CONSTRAINT "fk_task_man_task_man_fdd24798" FOREIGN KEY ("status_id") REFERENCES "task_management_taskstatus" ("id") ON DELETE CASCADE;
CREATE TABLE IF NOT EXISTS "taskchain_taskvisibility_status_through" ("status_id" INT NOT NULL REFERENCES "amocrm_statuses" ("id") ON DELETE CASCADE,"task_chain_id" INT NOT NULL REFERENCES "task_management_taskchain" ("id") ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS "taskchain_status_through" ("task_chain_id" INT NOT NULL REFERENCES "task_management_taskchain" ("id") ON DELETE CASCADE,"status_id" INT NOT NULL REFERENCES "amocrm_statuses" ("id") ON DELETE CASCADE);
-- downgrade --
DROP TABLE IF EXISTS "taskchain_status_through";
DROP TABLE IF EXISTS "taskchain_taskvisibility_status_through";
ALTER TABLE "task_management_button" DROP CONSTRAINT "fk_task_man_task_man_fdd24798";
ALTER TABLE "task_management_button" ALTER COLUMN "style" TYPE JSONB USING "style"::JSONB;
ALTER TABLE "task_management_button" ALTER COLUMN "status_id" TYPE INT USING "status_id"::INT;
ALTER TABLE "task_management_taskchain" ADD "task_visibility" JSONB;
ALTER TABLE "task_management_taskchain" ADD "booking_substage" VARCHAR(100);
ALTER TABLE "task_management_taskinstance" DROP COLUMN "sensei_pid";
ALTER TABLE "task_management_taskinstance" ALTER COLUMN "comment" SET NOT NULL;
