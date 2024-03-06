from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_testbooking" ADD "amocrm_id" VARCHAR(50) NOT NULL;
        ALTER TABLE "booking_testbooking" ALTER COLUMN "status" SET DEFAULT 'in_amo';
        CREATE INDEX "idx_booking_tes_amocrm__f54d31" ON "booking_testbooking" ("amocrm_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_booking_tes_amocrm__f54d31";
        ALTER TABLE "booking_testbooking" DROP COLUMN "amocrm_id";
        ALTER TABLE "booking_testbooking" ALTER COLUMN "status" SET DEFAULT 'not_in_amo';"""
