from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_user" ADD "date_assignment_loyalty_status" TIMESTAMPTZ;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_user" DROP COLUMN IF EXISTS "date_assignment_loyalty_status";
        """
