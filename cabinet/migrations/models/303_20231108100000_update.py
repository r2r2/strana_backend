from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "taskchain_interchangeable_through" (
            "id" SERIAL PRIMARY KEY,
            "task_chain_id" INT NOT NULL REFERENCES "task_management_taskchain" ("id") ON DELETE CASCADE,
            "interchangeable_chain_id" INT NOT NULL REFERENCES "task_management_taskchain" ("id") ON DELETE SET NULL
            );
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "taskchain_interchangeable_through";
        """
