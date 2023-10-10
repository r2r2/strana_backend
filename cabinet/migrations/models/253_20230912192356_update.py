from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "booking_acquiring" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "is_active" BOOL NOT NULL  DEFAULT False,
    "username" VARCHAR(100) NOT NULL,
    "password" VARCHAR(200) NOT NULL,
    "city_id" INT NOT NULL REFERENCES "cities_city" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_booking_acq_city_id_f58770" UNIQUE ("city_id", "is_active")
);
COMMENT ON COLUMN "booking_acquiring"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "booking_acquiring"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "booking_acquiring"."id" IS 'ID';
COMMENT ON COLUMN "booking_acquiring"."is_active" IS 'Активный';
COMMENT ON COLUMN "booking_acquiring"."username" IS 'Имя пользователя';
COMMENT ON COLUMN "booking_acquiring"."password" IS 'Пароль';
COMMENT ON COLUMN "booking_acquiring"."city_id" IS 'Город';
COMMENT ON TABLE "booking_acquiring" IS 'Эквайринги';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "booking_acquiring";"""
