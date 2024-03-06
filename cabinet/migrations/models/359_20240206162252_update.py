from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE booking_event_history ADD COLUMN 
    "signed_offer_id" INT REFERENCES "documents_document_archive" ("id") ON DELETE SET NULL;
COMMENT ON COLUMN "booking_event_history"."signed_offer_id" IS 'Шаблон подписанной оферты';
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE booking_event_history DROP COLUMN "signed_offer_id" """
