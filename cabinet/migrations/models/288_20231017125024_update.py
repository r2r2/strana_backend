from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    ALTER TABLE "notifications_event_sms_notification" ADD "only_for_online" BOOL NOT NULL  DEFAULT False;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "notifications_event_sms_notification" DROP COLUMN "only_for_online";
        """
