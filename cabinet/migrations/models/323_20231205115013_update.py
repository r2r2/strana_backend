from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "mortgage_ticket_types" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(100),
    "amocrm_id" BIGINT UNIQUE
);
COMMENT ON COLUMN "mortgage_ticket_types"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_ticket_types"."title" IS 'Название';
COMMENT ON COLUMN "mortgage_ticket_types"."amocrm_id" IS 'ID в AmoCRM';
COMMENT ON TABLE "mortgage_ticket_types" IS 'ID в AmoCRM';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """;
        DROP TABLE IF EXISTS "mortgage_ticket_types";"""