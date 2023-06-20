-- upgrade --
CREATE TABLE IF NOT EXISTS "task_management_logs" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "state_before" JSONB,
    "state_after" JSONB,
    "state_difference" JSONB,
    "content" TEXT,
    "error_data" TEXT,
    "response_data" TEXT,
    "use_case" VARCHAR(200),
    "task_instance_id" INT REFERENCES "task_management_taskinstance" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "task_management_logs"."id" IS 'ID';
COMMENT ON COLUMN "task_management_logs"."created" IS 'Создано';
COMMENT ON COLUMN "task_management_logs"."state_before" IS 'Состояние до';
COMMENT ON COLUMN "task_management_logs"."state_after" IS 'Состояние после';
COMMENT ON COLUMN "task_management_logs"."state_difference" IS 'Разница состояний';
COMMENT ON COLUMN "task_management_logs"."content" IS 'Контент';
COMMENT ON COLUMN "task_management_logs"."error_data" IS 'Данные ошибки';
COMMENT ON COLUMN "task_management_logs"."response_data" IS 'Данные ответа';
COMMENT ON COLUMN "task_management_logs"."use_case" IS 'Сценарий';
COMMENT ON COLUMN "task_management_logs"."task_instance_id" IS 'Экземпляр задания';
COMMENT ON TABLE "task_management_logs" IS 'Лог задачи';
-- downgrade --
DROP TABLE IF EXISTS "task_management_logs";
