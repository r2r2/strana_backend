from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS notifications_sberbank_invoice_log (
            id SERIAL NOT NULL PRIMARY KEY,
            amocrm_id INT NOT NULL,
            sent_date timestamptz NOT NULL,
            sent_email VARCHAR(64) NOT NULL,
            sent_status BOOLEAN NOT NULL,
            sent_error TEXT NULL,
            created_at timestamptz NOT NULL,
            updated_at timestamptz NOT NULL
        );
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
    DROP TABLE IF EXISTS notifications_sberbank_invoice_log;
    """
