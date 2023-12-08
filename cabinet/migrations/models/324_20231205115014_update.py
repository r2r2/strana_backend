from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "mortgage_calculator_ticket" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" timestamp with time zone DEFAULT NOW()
);
COMMENT ON COLUMN "mortgage_calculator_ticket"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_calculator_ticket"."created_at" IS 'Дата и время создания';
COMMENT ON TABLE "mortgage_calculator_ticket" IS ' Ticket под ипотечный калькулятор';
        CREATE TABLE IF NOT EXISTS "mortgage_calcutator_ticket_booking_through" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mortgage_ticket_id" INT NOT NULL REFERENCES "mortgage_calculator_ticket" ("id") ON DELETE CASCADE,
    "booking_id" INT NOT NULL REFERENCES "booking_booking" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "mortgage_calcutator_ticket_booking_through"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_calcutator_ticket_booking_through"."mortgage_ticket_id" IS 'Тикет';
COMMENT ON COLUMN "mortgage_calcutator_ticket_booking_through"."booking_id" IS 'Сделка';
COMMENT ON TABLE "mortgage_calcutator_ticket_booking_through" IS 'Отношение тикетов к сделкам';
        CREATE TABLE IF NOT EXISTS "mortgage_calcutator_ticket_to_ticket_type_through" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mortgage_ticket_id" INT NOT NULL REFERENCES "mortgage_calculator_ticket" ("id") ON DELETE CASCADE,
    "mortgage_ticket_type_id" INT NOT NULL REFERENCES "mortgage_ticket_types" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "mortgage_calcutator_ticket_to_ticket_type_through"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_calcutator_ticket_to_ticket_type_through"."mortgage_ticket_id" IS 'Тикет';
COMMENT ON COLUMN "mortgage_calcutator_ticket_to_ticket_type_through"."mortgage_ticket_type_id" IS 'Тип заявки';
COMMENT ON TABLE "mortgage_calcutator_ticket_to_ticket_type_through" IS 'Отношения Тикетов к типам';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """;
        DROP TABLE IF EXISTS "mortgage_calculator_ticket" CASCADE;
        DROP TABLE IF EXISTS "mortgage_calcutator_ticket_booking_through";
        DROP TABLE IF EXISTS "mortgage_calcutator_ticket_to_ticket_type_through";"""