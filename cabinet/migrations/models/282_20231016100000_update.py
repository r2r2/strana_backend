from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "event_list" ADD COLUMN IF NOT EXISTS "start_showing_date" DATE;
        ALTER TABLE "event_list" ALTER COLUMN "event_date" TYPE DATE USING "event_date"::DATE;
        ALTER TABLE "event_participant_list" ADD "group_id" INT;
        ALTER TABLE "event_participant_list" ADD "timeslot" VARCHAR(255);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "event_list" DROP COLUMN IF EXISTS "start_showing_date";
        ALTER TABLE "event_list" ALTER COLUMN "event_date" TYPE TIMESTAMPTZ USING "event_date"::TIMESTAMPTZ;
        ALTER TABLE "event_participant_list" DROP COLUMN "group_id";
        ALTER TABLE "event_participant_list" DROP COLUMN "timeslot";"""
