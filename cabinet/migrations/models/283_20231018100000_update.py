from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "task_management_button_detail_view" ADD COLUMN IF NOT EXISTS "slug_step" VARCHAR(100);
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "task_management_button_detail_view" DROP COLUMN "slug_step";"""
