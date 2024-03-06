from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE INDEX "idx_booking_boo_booking_8c1e51" ON "booking_bookinglog" ("booking_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_booking_boo_booking_8c1e51";
"""
