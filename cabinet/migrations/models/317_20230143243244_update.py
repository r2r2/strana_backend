from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "mortgage_calculator_banks" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "bank_name" TEXT NOT NULL,
    "bank_icon" VARCHAR(300),
    "priority" INT NOT NULL  DEFAULT 0,
    "external_code" TEXT NOT NULL
);
COMMENT ON COLUMN "mortgage_calculator_banks"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_calculator_banks"."bank_name" IS 'Имя банка';
COMMENT ON COLUMN "mortgage_calculator_banks"."bank_icon" IS 'Иконка банка';
COMMENT ON COLUMN "mortgage_calculator_banks"."priority" IS 'Приоритет';
COMMENT ON COLUMN "mortgage_calculator_banks"."external_code" IS 'Внешний код';
COMMENT ON TABLE "mortgage_calculator_banks" IS 'Банки под ипотечный калькулятор.';
        CREATE TABLE IF NOT EXISTS "mortgage_calculator_program" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "program_name" TEXT NOT NULL,
    "priority" INT NOT NULL  DEFAULT 0,
    "external_code" TEXT NOT NULL
);
COMMENT ON COLUMN "mortgage_calculator_program"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_calculator_program"."program_name" IS 'Имя банка';
COMMENT ON COLUMN "mortgage_calculator_program"."priority" IS 'Приоритет';
COMMENT ON COLUMN "mortgage_calculator_program"."external_code" IS 'Внешний код';
COMMENT ON TABLE "mortgage_calculator_program" IS 'Программы под ипотечный калькулятор.';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "mortgage_calculator_banks";
        DROP TABLE IF EXISTS "mortgage_calculator_program";"""
