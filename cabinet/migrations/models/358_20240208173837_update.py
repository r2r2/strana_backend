from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_task_manage_booking_43f6a2" 
        ON "task_management_taskinstance" ("booking_id", "status_id");
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "uid_task_manage_booking_43f6a2";
        """
