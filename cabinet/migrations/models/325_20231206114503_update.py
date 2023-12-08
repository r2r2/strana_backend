from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "mortgage_calculator_developer_ticket" (
    "id" SERIAL NOT NULL PRIMARY KEY
);
COMMENT ON COLUMN "mortgage_calculator_developer_ticket"."id" IS 'ID';
COMMENT ON TABLE "mortgage_calculator_developer_ticket" IS 'Заявка через застройщика';
        CREATE TABLE "mortgage_calculator_dev_ticket_condition_through" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mortgage_condition_id" INT NOT NULL REFERENCES "mortgage_calcutator_condition" ("id") ON DELETE CASCADE,
    "mortgage_dev_ticket_id" INT NOT NULL REFERENCES "mortgage_calculator_developer_ticket" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "mortgage_calculator_dev_ticket_condition_through"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_calculator_dev_ticket_condition_through"."mortgage_condition_id" IS 'Условие';
COMMENT ON COLUMN "mortgage_calculator_dev_ticket_condition_through"."mortgage_dev_ticket_id" IS 'Тикет через застройщика';
COMMENT ON TABLE "mortgage_calculator_dev_ticket_condition_through" IS 'Условия в калькуляторе';
        CREATE TABLE "mortgage_calculator_ticket_status_through" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mortgage_status_id" INT NOT NULL REFERENCES "mortgage_application_status" ("id") ON DELETE CASCADE,
    "mortgage_dev_application_id" INT NOT NULL REFERENCES "mortgage_calculator_developer_ticket" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "mortgage_calculator_ticket_status_through"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_calculator_ticket_status_through"."mortgage_status_id" IS 'Статус';
COMMENT ON COLUMN "mortgage_calculator_ticket_status_through"."mortgage_dev_application_id" IS 'Тикет через застройщика';
COMMENT ON TABLE "mortgage_calculator_ticket_status_through" IS 'Статус заявки';
        CREATE TABLE "mortgage_calculator_dev_ticket_form_through" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mortgage_form_id" INT NOT NULL REFERENCES "mortgage_form" ("id") ON DELETE CASCADE,
    "mortgage_dev_ticket_id" INT NOT NULL REFERENCES "mortgage_calculator_developer_ticket" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "mortgage_calculator_dev_ticket_form_through"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_calculator_dev_ticket_form_through"."mortgage_form_id" IS 'Форма';
COMMENT ON COLUMN "mortgage_calculator_dev_ticket_form_through"."mortgage_dev_ticket_id" IS 'Тикет через застройщика';
COMMENT ON TABLE "mortgage_calculator_dev_ticket_form_through" IS 'Форма заявки';
        CREATE TABLE "mortgage_calculator_dev_ticket_proposal_through" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mortgage_proposal_id" INT NOT NULL REFERENCES "mortgage_submitted_proposal" ("id") ON DELETE CASCADE,
    "mortgage_dev_ticket_id" INT NOT NULL REFERENCES "mortgage_calculator_developer_ticket" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "mortgage_calculator_dev_ticket_proposal_through"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_calculator_dev_ticket_proposal_through"."mortgage_proposal_id" IS 'Предложение';
COMMENT ON COLUMN "mortgage_calculator_dev_ticket_proposal_through"."mortgage_dev_ticket_id" IS 'Тикет через застройщика';
COMMENT ON TABLE "mortgage_calculator_dev_ticket_proposal_through" IS 'Подданные предложения на заявку';
        CREATE TABLE "mortgage_calculator_dev_ticket_to_ticket_through" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mortgage_ticket_id" INT NOT NULL REFERENCES "mortgage_calculator_ticket" ("id") ON DELETE CASCADE,
    "mortgage_dev_ticket_id" INT NOT NULL REFERENCES "mortgage_calculator_developer_ticket" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "mortgage_calculator_dev_ticket_to_ticket_through"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_calculator_dev_ticket_to_ticket_through"."mortgage_ticket_id" IS 'Тикет';
COMMENT ON COLUMN "mortgage_calculator_dev_ticket_to_ticket_through"."mortgage_dev_ticket_id" IS 'Тикет через застройщика (более общий)';
COMMENT ON TABLE "mortgage_calculator_dev_ticket_to_ticket_through" IS 'Отношение тикета через застройщика на тикет';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "mortgage_calculator_dev_ticket_proposal_through";
        DROP TABLE IF EXISTS "mortgage_calculator_ticket_status_through";
        DROP TABLE IF EXISTS "mortgage_calculator_dev_ticket_condition_through";
        DROP TABLE IF EXISTS "mortgage_calculator_dev_ticket_to_ticket_through";
        DROP TABLE IF EXISTS "mortgage_calculator_dev_ticket_form_through";
        DROP TABLE IF EXISTS "mortgage_calculator_developer_ticket";"""
