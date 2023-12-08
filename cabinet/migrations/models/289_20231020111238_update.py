from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "booking_booking_client_user_through" (
    "booking_id" INT NOT NULL REFERENCES "booking_booking" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users_user" ("id") ON DELETE CASCADE,
    "is_main" BOOL NOT NULL  DEFAULT False
);
COMMENT ON COLUMN "booking_booking_client_user_through"."is_main" IS 'Главный клиент сделки';
COMMENT ON COLUMN "booking_booking_client_user_through"."booking_id" IS 'Сделка';
COMMENT ON COLUMN "booking_booking_client_user_through"."user_id" IS 'Клиент';
COMMENT ON TABLE "booking_booking_client_user_through" IS 'Все пользователи которые участвуют в сделке';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "booking_booking_client_user_through";"""
