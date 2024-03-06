from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_booking" ADD "property_lk_datetime" TIMESTAMPTZ;
        ALTER TABLE "booking_booking" ADD "property_lk" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "booking_booking" ADD "property_lk_on_time" BOOL NOT NULL  DEFAULT False;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_booking" DROP COLUMN "property_lk_datetime";
        ALTER TABLE "booking_booking" DROP COLUMN "property_lk";
        ALTER TABLE "booking_booking" DROP COLUMN "property_lk_on_time";"""
