from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_testbooking" ALTER COLUMN "last_check_at" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_testbooking" ALTER COLUMN "last_check_at" SET NOT NULL;"""
