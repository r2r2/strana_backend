from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "mortgage_calculator_developer_ticket" ADD COLUMN IF NOT EXISTS "booking_id" BIGINT REFERENCES "booking_booking" ("id") ON DELETE CASCADE;
        ALTER TABLE "mortgage_calculator_developer_ticket" ADD COLUMN IF NOT EXISTS "ticket_type_id" INT REFERENCES "mortgage_ticket_types" ("id") ON DELETE CASCADE;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "mortgage_calculator_developer_ticket" DROP COLUMN IF EXISTS "booking_id";
        ALTER TABLE "mortgage_calculator_developer_ticket" DROP COLUMN IF EXISTS "ticket_type_id";
        """
