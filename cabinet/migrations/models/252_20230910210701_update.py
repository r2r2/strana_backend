from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_booking" ADD "pay_extension_number" INT;
        ALTER TABLE "settings_booking_settings" ADD "pay_extension_value" INT NOT NULL  DEFAULT 10;
        ALTER TABLE "settings_booking_settings" ADD "pay_extension_number" INT NOT NULL  DEFAULT 1;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_booking" DROP COLUMN "pay_extension_number";
        ALTER TABLE "settings_booking_settings" DROP COLUMN "pay_extension_value";
        ALTER TABLE "settings_booking_settings" DROP COLUMN "pay_extension_number";"""
