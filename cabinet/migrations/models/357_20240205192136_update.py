from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_event_history" ALTER COLUMN "group_status_until" DROP NOT NULL;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_event_history" ALTER COLUMN "group_status_until" SET NOT NULL;
        """
