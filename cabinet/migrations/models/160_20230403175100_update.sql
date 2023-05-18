-- upgrade --
ALTER TABLE "task_management_taskstatus" ALTER COLUMN "priority" TYPE INT USING "priority"::INT;
-- downgrade --
ALTER TABLE "task_management_taskstatus" ALTER COLUMN "priority" TYPE SMALLINT USING "priority"::SMALLINT;
