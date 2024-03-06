from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    ALTER TABLE booking_booking
        ADD COLUMN loyalty_discount_name VARCHAR(150),
        ADD COLUMN loyalty_discount DECIMAL(15, 3);
        COMMENT ON COLUMN "booking_booking"."loyalty_discount_name" IS 'Применённый промокод/скидка';
        COMMENT ON COLUMN "booking_booking"."loyalty_discount" IS 'Скидка по промокоду (руб.)';
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
    ALTER TABLE booking_booking
    DROP COLUMN IF EXISTS loyalty_discount_name;
    ALTER TABLE booking_booking
    DROP COLUMN IF EXISTS loyalty_discount;
"""