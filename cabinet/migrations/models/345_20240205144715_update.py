from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "mortgage_application_archive" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "external_code" INT NOT NULL,
    "booking_id" INT NOT NULL,
    "mortgage_application_status_until" VARCHAR(150) NOT NULL,
    "mortgage_application_status_after" VARCHAR(150) NOT NULL,
    "status_change_date" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "mortgage_application_archive"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_application_archive"."external_code" IS 'ID заявки в ИК';
COMMENT ON COLUMN "mortgage_application_archive"."booking_id" IS 'ID брони';
COMMENT ON COLUMN "mortgage_application_archive"."mortgage_application_status_until" IS 'Статус заявки на ипотеку До';
COMMENT ON COLUMN "mortgage_application_archive"."mortgage_application_status_after" IS 'Статус заявки на ипотеку После';
COMMENT ON COLUMN "mortgage_application_archive"."status_change_date" IS 'Время изменения статуса';
ALTER TABLE booking_event_history
    ADD COLUMN mortgage_ticket_inform_id INT REFERENCES mortgage_application_archive (id) ON DELETE SET NULL;
    COMMENT ON COLUMN booking_event_history."mortgage_ticket_inform_id" IS 'Архив заявки на ипотеку';
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE booking_event_history
            DROP COLUMN mortgage_ticket_inform_id;
        DROP TABLE IF EXISTS "mortgage_application_archive";"""
