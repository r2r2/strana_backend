from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "task_management_logs" ADD "task_chain_id" INT;
        ALTER TABLE "task_management_logs" ADD "booking_id" INT;
        ALTER TABLE "task_management_logs" ADD CONSTRAINT "fk_task_man_task_man_b3e2a327" FOREIGN KEY ("task_chain_id") REFERENCES "task_management_taskchain" ("id") ON DELETE CASCADE;
        ALTER TABLE "task_management_logs" ADD CONSTRAINT "fk_task_man_booking__20c3d4a0" FOREIGN KEY ("booking_id") REFERENCES "booking_booking" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "task_management_logs" DROP CONSTRAINT "fk_task_man_booking__20c3d4a0";
        ALTER TABLE "task_management_logs" DROP CONSTRAINT "fk_task_man_task_man_b3e2a327";
        ALTER TABLE "task_management_logs" DROP COLUMN "task_chain_id";
        ALTER TABLE "task_management_logs" DROP COLUMN "booking_id";"""
