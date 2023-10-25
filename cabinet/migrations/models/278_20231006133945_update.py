from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "payments_mortgage_types" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(100),
    "amocrm_id" BIGINT  UNIQUE
);
COMMENT ON COLUMN "payments_mortgage_types"."id" IS 'ID';
COMMENT ON COLUMN "payments_mortgage_types"."title" IS 'Название';
COMMENT ON COLUMN "payments_mortgage_types"."amocrm_id" IS 'ID в AmoCRM';
COMMENT ON TABLE "payments_mortgage_types" IS 'Тип ипотеки';
        ALTER TABLE "payments_payment_method" ADD "amocrm_id" BIGINT  UNIQUE;
        ALTER TABLE "booking_booking" ADD "mortgage_type_id" INT;
        CREATE UNIQUE INDEX "uid_payments_pa_amocrm__7e5021" ON "payments_payment_method" ("amocrm_id");
        ALTER TABLE "booking_booking" ADD CONSTRAINT "fk_booking__payments_cb977dcb" FOREIGN KEY ("mortgage_type_id") REFERENCES "payments_mortgage_types" ("id") ON DELETE SET NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_payments_pa_amocrm__7e5021";
        ALTER TABLE "booking_booking" DROP CONSTRAINT "fk_booking__payments_cb977dcb";
        ALTER TABLE "booking_booking" DROP COLUMN "mortgage_type_id";
        ALTER TABLE "payments_payment_method" DROP COLUMN "amocrm_id";
        DROP TABLE IF EXISTS "payments_mortgage_types";"""
