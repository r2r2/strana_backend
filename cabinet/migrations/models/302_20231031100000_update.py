from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "task_management_group_statuses" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "name" VARCHAR(255) NOT NULL,
            "priority" INT NOT NULL DEFAULT 0,
            "color" VARCHAR(16),
            "slug" VARCHAR(255) NOT NULL,
            "task_chain_id" INT NOT NULL REFERENCES "task_management_taskchain" ("id") ON DELETE CASCADE,
            "created_at" timestamp with time zone DEFAULT NOW(),
            "updated_at" timestamp with time zone DEFAULT NOW()
        );
        COMMENT ON COLUMN "task_management_group_statuses"."priority" IS 'Сортировка';
        COMMENT ON TABLE "task_management_group_statuses" IS 'Группирующие статусы для задач';
        
        CREATE TABLE IF NOT EXISTS "task_management_group_status_through" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "task_group_status_id" INT NOT NULL REFERENCES "task_management_group_statuses" ("id") ON DELETE CASCADE,
            "task_status_id" INT NOT NULL REFERENCES "task_management_taskstatus" ("id") ON DELETE CASCADE
        );
        COMMENT ON COLUMN "task_management_group_status_through"."id" IS 'ID';
        COMMENT ON COLUMN "task_management_group_status_through"."task_group_status_id" IS 'Группа статусов задач';
        COMMENT ON COLUMN "task_management_group_status_through"."task_status_id" IS 'Статус задачи';
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "task_management_group_status_through";
        DROP TABLE IF EXISTS "task_management_group_statuses";
        """
