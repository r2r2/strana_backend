from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    CREATE TABLE IF NOT EXISTS task_management_button_detail_view (
        id SERIAL PRIMARY KEY,
        label VARCHAR(100),
        style VARCHAR(20),
        slug VARCHAR(100),
        priority INT,
        task_status INT REFERENCES task_management_taskstatus(id) ON DELETE SET NULL,
        created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    
    CREATE TABLE IF NOT EXISTS task_management_taskstatus_buttons_detail (
        id SERIAL PRIMARY KEY,
        button_id INT REFERENCES task_management_button_detail_view(id) ON DELETE CASCADE,
        task_status_id INT REFERENCES task_management_taskstatus(id) ON DELETE CASCADE
    );
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
    DROP TABLE IF EXISTS task_management_taskstatus_buttons_detail;
    DROP TABLE IF EXISTS task_management_button_detail_view;
    """
