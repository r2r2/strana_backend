from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_booking" RENAME COLUMN "payment_method_id" TO "amo_payment_method_id";
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_booking" RENAME COLUMN "amo_payment_method_id" TO "payment_method_id";
        """
