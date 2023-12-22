from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "notifications_sberbank_invoice_log" ALTER COLUMN "amocrm_id" DROP NOT NULL;
        ALTER TABLE "notifications_sberbank_invoice_log" ALTER COLUMN "sent_email" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "notifications_sberbank_invoice_log" ALTER COLUMN "amocrm_id" SET NOT NULL;
        ALTER TABLE "notifications_sberbank_invoice_log" ALTER COLUMN "sent_email" SET NOT NULL;
        """
