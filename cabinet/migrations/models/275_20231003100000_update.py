from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    CREATE TABLE IF NOT EXISTS event_list (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        token TEXT,
        event_date TIMESTAMP,
        title VARCHAR(255),
        subtitle VARCHAR(255)
    );
    
    CREATE TABLE IF NOT EXISTS event_participant_list (
        id SERIAL PRIMARY KEY,
        phone VARCHAR(36),
        event_id INT REFERENCES event_list(id) ON DELETE SET NULL,
        code VARCHAR(255)
    );
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
    DROP TABLE IF EXISTS event_participant_list;
    DROP TABLE IF EXISTS event_list;
    """
