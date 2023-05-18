-- upgrade --
CREATE TABLE IF NOT EXISTS "task_management_taskchain" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "booking_substage" VARCHAR(100),
    "task_visibility" JSONB
);
CREATE TABLE IF NOT EXISTS "task_management_taskstatus" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT NOT NULL,
    "type" VARCHAR(20) NOT NULL,
    "priority" SMALLINT NOT NULL,
    "slug" VARCHAR(255) NOT NULL,
    "tasks_chain_id" INT NOT NULL REFERENCES "task_management_taskchain" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "task_management_taskinstance" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "comment" TEXT NOT NULL,
    "task_amocrmid" VARCHAR(255),
    "booking_id" INT NOT NULL REFERENCES "booking_booking" ("id") ON DELETE CASCADE,
    "status_id" INT NOT NULL REFERENCES "task_management_taskstatus" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "task_management_button" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "label" VARCHAR(100) NOT NULL,
    "style" JSONB,
    "slug" VARCHAR(100),
    "status_id" INT REFERENCES "task_management_taskstatus" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "task_management_taskchain"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "task_management_taskchain"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "task_management_taskchain"."id" IS 'ID';
COMMENT ON COLUMN "task_management_taskchain"."name" IS 'Название цепочки заданий';
COMMENT ON COLUMN "task_management_taskchain"."booking_substage" IS 'Первое задание в цепочке будет создано при достижении сделкой данного статуса';
COMMENT ON COLUMN "task_management_taskchain"."task_visibility" IS 'Задание будет видно только в данных статусах, в последующих статусах оно будет не видно';
COMMENT ON TABLE "task_management_taskchain" IS 'Цепочка заданий';
COMMENT ON COLUMN "task_management_taskinstance"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "task_management_taskinstance"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "task_management_taskinstance"."id" IS 'ID';
COMMENT ON COLUMN "task_management_taskinstance"."comment" IS 'Комментарий администратора АМО';
COMMENT ON COLUMN "task_management_taskinstance"."task_amocrmid" IS 'ID задачи в АМО';
COMMENT ON COLUMN "task_management_taskinstance"."booking_id" IS 'ID сущности, в которой будет выводиться задание';
COMMENT ON COLUMN "task_management_taskinstance"."status_id" IS 'Логика переходов заданий между шаблонами зашита и описана в проектной документации.';
COMMENT ON TABLE "task_management_taskinstance" IS 'Задача';;
COMMENT ON COLUMN "task_management_taskstatus"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "task_management_taskstatus"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "task_management_taskstatus"."id" IS 'ID';
COMMENT ON COLUMN "task_management_taskstatus"."name" IS 'Выводится в списке сущностей и в карточке сущности';
COMMENT ON COLUMN "task_management_taskstatus"."description" IS 'Выводится в карточке сущности.';
COMMENT ON COLUMN "task_management_taskstatus"."type" IS 'Влияет на выводимую иконку';
COMMENT ON COLUMN "task_management_taskstatus"."priority" IS 'Чем больше приоритет, тем выше будет выводиться задание в карточке (если заданий несколько)';
COMMENT ON COLUMN "task_management_taskstatus"."slug" IS 'Символьный код';
COMMENT ON COLUMN "task_management_taskstatus"."tasks_chain_id" IS 'Определяет триггер запуска первого задания в цепочке (задается в цепочке заданий). Логика переходов заданий по цепочке зашита в коде.';
COMMENT ON TABLE "task_management_taskstatus" IS 'Статус задачи';
COMMENT ON COLUMN "task_management_button"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "task_management_button"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "task_management_button"."id" IS 'ID';
COMMENT ON COLUMN "task_management_button"."label" IS 'Название кнопки';
COMMENT ON COLUMN "task_management_button"."style" IS 'Стиль кнопки';
COMMENT ON COLUMN "task_management_button"."slug" IS 'Слаг кнопки';
COMMENT ON COLUMN "task_management_button"."status_id" IS 'Статус, к которому привязана кнопка';
-- downgrade --
DROP TABLE IF EXISTS "task_management_taskchain";
DROP TABLE IF EXISTS "task_management_taskinstance";
DROP TABLE IF EXISTS "task_management_taskstatus";
DROP TABLE IF EXISTS "task_management_button";
