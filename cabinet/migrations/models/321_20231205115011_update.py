from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "mortgage_calcutator_condition" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "cost_before" DOUBLE PRECISION NOT NULL  DEFAULT 0,
    "initial_fee_before" DOUBLE PRECISION NOT NULL  DEFAULT 0,
    "until" DOUBLE PRECISION NOT NULL  DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "proof_of_income" VARCHAR(50) NOT NULL
);
COMMENT ON COLUMN "mortgage_calcutator_condition"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_calcutator_condition"."cost_before" IS 'Стоимость до';
COMMENT ON COLUMN "mortgage_calcutator_condition"."initial_fee_before" IS 'Первоначальный взнос до';
COMMENT ON COLUMN "mortgage_calcutator_condition"."until" IS 'Срок до';
COMMENT ON COLUMN "mortgage_calcutator_condition"."created_at" IS 'Дата и время создания';
COMMENT ON COLUMN "mortgage_calcutator_condition"."proof_of_income" IS 'Подтверждение дохода';
COMMENT ON TABLE "mortgage_calcutator_condition" IS 'Условия калькулятора.';
        CREATE TABLE IF NOT EXISTS "mortgage_calсutator_condition_bank_through" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mortgage_condition_id" INT NOT NULL REFERENCES "mortgage_calcutator_condition" ("id") ON DELETE CASCADE,
    "mortgage_bank_id" INT NOT NULL REFERENCES "mortgage_calculator_banks" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "mortgage_calсutator_condition_bank_through"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_calсutator_condition_bank_through"."mortgage_condition_id" IS 'Условия';
COMMENT ON COLUMN "mortgage_calсutator_condition_bank_through"."mortgage_bank_id" IS 'Банки';
COMMENT ON TABLE "mortgage_calсutator_condition_bank_through" IS 'Отношения ип калькулят условий к банкам';
        CREATE TABLE IF NOT EXISTS "mortgage_calсutator_condition_program_through" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mortgage_condition_id" INT NOT NULL REFERENCES "mortgage_calcutator_condition" ("id") ON DELETE CASCADE,
    "mortgage_program_id" INT NOT NULL REFERENCES "mortgage_calculator_program" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "mortgage_calсutator_condition_program_through"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_calсutator_condition_program_through"."mortgage_condition_id" IS 'Условия';
COMMENT ON COLUMN "mortgage_calсutator_condition_program_through"."mortgage_program_id" IS 'Программы';
COMMENT ON TABLE "mortgage_calсutator_condition_program_through" IS 'Отношения ип калькулят условий к программам';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "mortgage_calсutator_condition_program_through";
        DROP TABLE IF EXISTS "mortgage_calсutator_condition_bank_through";
        DROP TABLE IF EXISTS "mortgage_canlutator_submitted_proposal_offer_through";"""