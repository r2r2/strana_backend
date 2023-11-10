from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "notifications_event_sms_notification" DROP COLUMN "days";
        ALTER TABLE "event_event" ADD "time_to_send_sms_before" TIMESTAMPTZ;
        ALTER TABLE "event_event" ADD "time_to_send_sms_after" TIMESTAMPTZ;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "event_event" DROP COLUMN "time_to_send_sms_before";
        ALTER TABLE "event_event" DROP COLUMN "time_to_send_sms_after";
        ALTER TABLE "notifications_event_sms_notification" ADD "days" DOUBLE PRECISION;"""
