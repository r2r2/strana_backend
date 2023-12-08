from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "mortage_calculator_offer" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "offer_name" TEXT NOT NULL,
    "external_code" TEXT NOT NULL,
    "payment_per_month" DOUBLE PRECISION NOT NULL  DEFAULT 0,
    "interest_rate" DOUBLE PRECISION NOT NULL  DEFAULT 0,
    "credit_term" DOUBLE PRECISION NOT NULL  DEFAULT 0
);
COMMENT ON COLUMN "mortage_calculator_offer"."id" IS 'ID';
COMMENT ON COLUMN "mortage_calculator_offer"."offer_name" IS 'Названеи оффера';
COMMENT ON COLUMN "mortage_calculator_offer"."external_code" IS 'Внешний код';
COMMENT ON COLUMN "mortage_calculator_offer"."payment_per_month" IS 'платеж в месяц';
COMMENT ON COLUMN "mortage_calculator_offer"."interest_rate" IS 'Процентная ставка';
COMMENT ON COLUMN "mortage_calculator_offer"."credit_term" IS 'Срок кредита';
COMMENT ON TABLE "mortage_calculator_offer" IS '# Программы под ипотечный калькулятор.';
        CREATE TABLE IF NOT EXISTS "mortage_calculator_offers_banks_through" (
    "mortagebank_id" INT NOT NULL REFERENCES "mortage_calculator_banks" ("id") ON DELETE CASCADE,
    "mortageoffer_id" INT NOT NULL REFERENCES "mortage_calculator_offer" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "mortage_calculator_offers_banks_through" IS 'банки';
        CREATE TABLE IF NOT EXISTS "mortage_calculator_offers_program_through" (
    "mortageprogram_id" INT NOT NULL REFERENCES "mortage_calculator_program" ("id") ON DELETE CASCADE,
    "mortageoffer_id" INT NOT NULL REFERENCES "mortage_calculator_offer" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "mortage_calculator_offers_program_through";
        DROP TABLE IF EXISTS "mortage_calculator_offers_banks_through";
        DROP TABLE IF EXISTS "mortage_calculator_offer";"""