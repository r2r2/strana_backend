from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "booking_testbooking" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "status" VARCHAR(20)   DEFAULT 'not_in_amo',
    "info" TEXT,
    "last_check_at" TIMESTAMPTZ NOT NULL,
    "is_check_skipped" BOOL NOT NULL  DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "booking_id" INT REFERENCES "booking_booking" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_booking_tes_status_98580d" ON "booking_testbooking" ("status");
CREATE INDEX IF NOT EXISTS "idx_booking_tes_booking_fed246" ON "booking_testbooking" ("booking_id");
COMMENT ON COLUMN "booking_testbooking"."id" IS 'ID';
COMMENT ON COLUMN "booking_testbooking"."status" IS 'Статус';
COMMENT ON COLUMN "booking_testbooking"."info" IS 'Примечание';
COMMENT ON COLUMN "booking_testbooking"."last_check_at" IS 'Дата последней проверки';
COMMENT ON COLUMN "booking_testbooking"."is_check_skipped" IS 'Исключить из проверки';
COMMENT ON COLUMN "booking_testbooking"."created_at" IS 'Дата создания';
COMMENT ON COLUMN "booking_testbooking"."updated_at" IS 'Дата обновления';
COMMENT ON COLUMN "booking_testbooking"."booking_id" IS 'Бронирование';
COMMENT ON TABLE "booking_testbooking" IS 'Тестовое Бронирование';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "booking_testbooking";"""
