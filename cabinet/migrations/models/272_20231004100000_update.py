from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "task_management_taskinstance" ADD COLUMN IF NOT EXISTS "current_step" VARCHAR(255);
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "task_management_taskinstance" DROP COLUMN IF EXISTS "current_step";
        """
