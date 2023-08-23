-- upgrade --
CREATE TABLE IF NOT EXISTS "task_management_taskfields" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "type" VARCHAR(100)
);
COMMENT ON COLUMN "task_management_taskfields"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "task_management_taskfields"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "task_management_taskfields"."id" IS 'ID';
COMMENT ON COLUMN "task_management_taskfields"."name" IS 'Название поля';
COMMENT ON COLUMN "task_management_taskfields"."type" IS 'Тип поля';
COMMENT ON TABLE "task_management_taskfields" IS 'Поля заданий';;

INSERT INTO task_management_taskfields (name, type)
VALUES
    ('id', 'число'),
    ('comment', 'строка'),
    ('task_amocrmid', 'строка'),
    ('status', 'Связь с сущностью [Статус задачи]'),
    ('booking', 'Связь с сущностью [Бронирование]');

CREATE TABLE IF NOT EXISTS "taskchain_taskfields_through" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "task_chain_field_id" INT NOT NULL REFERENCES "task_management_taskchain" ("id") ON DELETE CASCADE,
    "task_field_id" INT NOT NULL REFERENCES "task_management_taskfields" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "taskchain_taskfields_through" IS 'Поля задания';
-- downgrade --
DROP TABLE IF EXISTS "taskchain_taskfields_through";
DROP TABLE IF EXISTS "task_management_taskfields";
