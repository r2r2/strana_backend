from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS taskchain_client_group_status_through (
            id SERIAL PRIMARY KEY,
            task_chain_id INT REFERENCES task_management_taskchain(id) ON DELETE CASCADE,
            client_group_status_id INT REFERENCES client_amocrm_group_statuses(id) ON DELETE CASCADE
        );
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS taskchain_client_group_status_through;
        """
