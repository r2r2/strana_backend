from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "settings_system_list" (
            "id" SERIAL PRIMARY KEY,
            "name" VARCHAR(255),
            "slug" VARCHAR(255)
            );
        CREATE TABLE IF NOT EXISTS "taskchain_systems_through" (
            "id" SERIAL PRIMARY KEY,
            "task_chain_id" INT NOT NULL REFERENCES "task_management_taskchain" ("id") ON DELETE CASCADE,
            "system_id" INT NOT NULL REFERENCES "settings_system_list" ("id") ON DELETE CASCADE
            );
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "taskchain_systems_through";
        DROP TABLE IF EXISTS "settings_system_list";
        """
