from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "booking_event_type" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "event_type_name" VARCHAR(150) NOT NULL,
    "slug" VARCHAR(100) NOT NULL
);
COMMENT ON TABLE "booking_event_type" IS 'Таблица типов событий';
COMMENT ON COLUMN "booking_event_type"."id" IS 'ID';
COMMENT ON COLUMN "booking_event_type"."event_type_name" IS 'Название';
COMMENT ON COLUMN "booking_event_type"."slug" IS 'Слаг';
CREATE TABLE IF NOT EXISTS "booking_event" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "event_name" VARCHAR(150) NOT NULL,
    "event_description" TEXT,
    "slug" VARCHAR(100) NOT NULL,
    "event_type_id" INT REFERENCES "booking_event_type" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "booking_event" IS 'Таблица событий';
COMMENT ON COLUMN "booking_event"."id" IS 'ID';
COMMENT ON COLUMN "booking_event"."event_name" IS 'Название';
COMMENT ON COLUMN "booking_event"."event_description" IS 'Описание';
COMMENT ON COLUMN "booking_event"."slug" IS 'Слаг';
COMMENT ON COLUMN "booking_event"."event_type_id" IS 'Тип события';
CREATE TABLE IF NOT EXISTS booking_event_history (
    id SERIAL PRIMARY KEY,
    booking_id INT REFERENCES booking_booking(id) ON DELETE CASCADE,
    actor VARCHAR(150) NOT NULL,
    event_id INT REFERENCES booking_event(id) ON DELETE SET NULL,
    event_slug VARCHAR(100) NOT NULL,
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type_name VARCHAR(150) NOT NULL,
    event_name VARCHAR(150) NOT NULL,
    event_description TEXT,
    group_status_until VARCHAR(150),
    group_status_after VARCHAR(150),
    task_name_until VARCHAR(150),
    task_name_after VARCHAR(150),
    event_status_until VARCHAR(150),
    event_status_after VARCHAR(150)
);
COMMENT ON TABLE booking_event_history IS 'Таблица истории событий бронирования';
COMMENT ON COLUMN booking_event_history.id IS 'ID';
COMMENT ON COLUMN booking_event_history.booking_id IS 'Сделка';
COMMENT ON COLUMN booking_event_history.actor IS 'Действующее лицо';
COMMENT ON COLUMN booking_event_history.event_id IS 'Событие';
COMMENT ON COLUMN booking_event_history.event_slug IS 'Слаг события';
COMMENT ON COLUMN booking_event_history.date_time IS 'Время';
COMMENT ON COLUMN booking_event_history.event_type_name IS 'Название типа события';
COMMENT ON COLUMN booking_event_history.event_name IS 'Название события';
COMMENT ON COLUMN booking_event_history.event_description IS 'Описание';
COMMENT ON COLUMN booking_event_history.group_status_until IS 'Групп. статус (Этап) До';
COMMENT ON COLUMN booking_event_history.group_status_after IS 'Групп. статус (Этап) После';
COMMENT ON COLUMN booking_event_history.task_name_until IS 'Название задачи До';
COMMENT ON COLUMN booking_event_history.task_name_after IS 'Название задачи После';
COMMENT ON COLUMN booking_event_history.event_status_until IS 'Статус встречи До';
COMMENT ON COLUMN booking_event_history.event_status_after IS 'Статус встречи После';
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "booking_event_history";
        DROP TABLE IF EXISTS "booking_event";
        DROP TABLE IF EXISTS "booking_event_type";"""
