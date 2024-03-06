from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "payments_mortgage_types" ADD "slug" VARCHAR(50)  UNIQUE;
        ALTER TABLE "payments_payment_method" ADD "slug" VARCHAR(50)  UNIQUE;
        ALTER TABLE "booking_booking" ADD "mortgage_offer" TEXT;
        ALTER TABLE "payments_mortgage_types" ADD "by_dev" BOOL NOT NULL  DEFAULT False;
        CREATE UNIQUE INDEX "uid_payments_mo_slug_63ecf0" ON "payments_mortgage_types" ("slug");
        CREATE UNIQUE INDEX "uid_payments_pa_slug_52ae03" ON "payments_payment_method" ("slug");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "uid_payments_pa_slug_52ae03";
        DROP INDEX "uid_payments_mo_slug_63ecf0";
        ALTER TABLE "payments_mortgage_types" DROP COLUMN "by_dev";
        ALTER TABLE "booking_booking" DROP COLUMN "mortgage_offer";
        ALTER TABLE "payments_mortgage_types" DROP COLUMN "slug";
        ALTER TABLE "payments_payment_method" DROP COLUMN "slug";"""
