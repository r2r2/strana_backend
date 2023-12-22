from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users_client_assign_maintenance" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "client_phone" VARCHAR(20) NOT NULL,
    "successful_assign" BOOL NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "users_client_assign_maintenance"."id" IS 'ID';
COMMENT ON COLUMN "users_client_assign_maintenance"."client_phone" IS 'Номер телефона';
COMMENT ON COLUMN "users_client_assign_maintenance"."successful_assign" IS 'Успешная проверка';
COMMENT ON COLUMN "users_client_assign_maintenance"."created_at" IS 'Дата и время создания';
COMMENT ON TABLE "users_client_assign_maintenance" IS 'Модель подтверждения закрепления клиента за агентом';
        CREATE TABLE IF NOT EXISTS "users_client_check_maintenance" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "client_phone" VARCHAR(20) NOT NULL,
    "successful_check" BOOL NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "users_client_check_maintenance"."id" IS 'ID';
COMMENT ON COLUMN "users_client_check_maintenance"."client_phone" IS 'Номер телефона';
COMMENT ON COLUMN "users_client_check_maintenance"."successful_check" IS 'Успешная проверка';
COMMENT ON COLUMN "users_client_check_maintenance"."created_at" IS 'Дата и время создания';
COMMENT ON TABLE "users_client_check_maintenance" IS 'Модель подтверждения закрепления клиента за агентом';
        CREATE TABLE IF NOT EXISTS "bookings_payments_maintenance" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "booking_amocrm_id" BIGINT NOT NULL,
    "successful_payment" BOOL NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "bookings_payments_maintenance"."id" IS 'ID';
COMMENT ON COLUMN "bookings_payments_maintenance"."booking_amocrm_id" IS 'ID в AmoCRM';
COMMENT ON COLUMN "bookings_payments_maintenance"."successful_payment" IS 'Успешная оплата';
COMMENT ON COLUMN "bookings_payments_maintenance"."created_at" IS 'Дата и время создания';
COMMENT ON TABLE "bookings_payments_maintenance" IS 'Данные по успешным оплатам по бронированию';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "users_client_assign_maintenance";
        DROP TABLE IF EXISTS "users_client_check_maintenance";
        DROP TABLE IF EXISTS "bookings_payments_maintenance";"""
