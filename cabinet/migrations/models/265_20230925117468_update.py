from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_booking" ADD "loyalty_point_amount" INT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_booking" DROP COLUMN "loyalty_point_amount";"""
