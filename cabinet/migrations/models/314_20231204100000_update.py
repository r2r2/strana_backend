from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "event_event" ADD "sms_template_id" INT;
        ALTER TABLE "event_event" ADD CONSTRAINT "fk_event_ev_notifica_262a37c8" FOREIGN KEY ("sms_template_id") REFERENCES "notifications_sms_notification" ("id") ON DELETE SET NULL;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "event_event" DROP CONSTRAINT "fk_event_ev_notifica_262a37c8";
        ALTER TABLE "event_event" DROP COLUMN "sms_template_id";
        """
