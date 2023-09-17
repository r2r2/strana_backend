from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "booking_source" (
        "id" SERIAL NOT NULL PRIMARY KEY,
        "name" VARCHAR(100) NOT NULL,
        "slug" VARCHAR(100) NOT NULL
        );
        COMMENT ON COLUMN "booking_source"."id" IS 'ID';
        COMMENT ON COLUMN "booking_source"."name" IS 'Название источника';
        COMMENT ON COLUMN "booking_source"."slug" IS 'Слаг источника';;
        
        insert into "booking_source" ("name", "slug")
        values
            ('Импортирован из AMOCRM', 'amocrm'),
            ('Бронирование через личный кабинет', 'lk_booking'),
            ('Закреплен в ЛК Брокера', 'lk_booking_assign'),
            ('Быстрое бронирование', 'fast_booking');
        
        CREATE TABLE IF NOT EXISTS "taskchain_booking_source_through" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "booking_source_id" INT NOT NULL REFERENCES "booking_source" ("id") ON DELETE CASCADE,
            "task_chain_id" INT NOT NULL REFERENCES "task_management_taskchain" ("id") ON DELETE CASCADE
        );
        COMMENT ON TABLE "taskchain_booking_source_through" IS 'Задачи из данной цепочки будут создаваться у данных типов сделок';
        COMMENT ON COLUMN "taskchain_booking_source_through"."id" IS 'ID';
        COMMENT ON COLUMN "taskchain_booking_source_through"."booking_source_id" IS 'Источник бронирования';
        COMMENT ON COLUMN "taskchain_booking_source_through"."task_chain_id" IS 'Цепочка заданий';
        COMMENT ON TABLE "taskchain_booking_source_through" IS 'Связующая таблица цепочки заданий и источника бронирования';
        
        alter table "booking_booking" add column if not exists "booking_source_id" INT REFERENCES "booking_source" ("id") ON DELETE CASCADE;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "taskchain_booking_source_through";
        DROP TABLE IF EXISTS "booking_source";
        alter table "booking_booking" drop column if exists "booking_source_id";
    """
