-- upgrade --
ALTER TABLE "task_management_taskchain" ADD IF NOT EXISTS "sensei_pid" INT;
ALTER TABLE "task_management_taskinstance" DROP COLUMN IF EXISTS "sensei_pid";
-- downgrade --
ALTER TABLE "task_management_taskchain" DROP COLUMN IF EXISTS "sensei_pid";
ALTER TABLE "task_management_taskinstance" ADD IF NOT EXISTS "sensei_pid" INT;
