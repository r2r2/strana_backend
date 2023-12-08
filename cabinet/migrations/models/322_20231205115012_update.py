from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "mortgage_calculator_condition_matrix" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "is_there_agent" BOOL NOT NULL  DEFAULT False,
    "default_value" BOOL NOT NULL  DEFAULT True,
    "is_apply_for_mortgage" VARCHAR(50) NOT NULL,
    "created_at" timestamp with time zone DEFAULT NOW(),
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "mortgage_calculator_condition_matrix"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_calculator_condition_matrix"."is_there_agent" IS 'Есть агент';
COMMENT ON COLUMN "mortgage_calculator_condition_matrix"."default_value" IS 'По умолчанию';
COMMENT ON COLUMN "mortgage_calculator_condition_matrix"."is_apply_for_mortgage" IS 'Можно ли подать заявку на ипотеку';
COMMENT ON COLUMN "mortgage_calculator_condition_matrix"."created_at" IS 'Дата и время создания';
COMMENT ON COLUMN "mortgage_calculator_condition_matrix"."updated_at" IS 'Дата и время обновления';
COMMENT ON TABLE "mortgage_calculator_condition_matrix" IS 'Матрциа условий калькулятора.';
        CREATE TABLE IF NOT EXISTS "mortgage_calсutator_matrix_condition_type_through" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mortgage_condition_id" INT NOT NULL REFERENCES "mortgage_calculator_condition_matrix" ("id") ON DELETE CASCADE,
    "mortgage_payments_types_id" INT NOT NULL REFERENCES "payments_mortgage_types" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "mortgage_calсutator_matrix_condition_type_through"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_calсutator_matrix_condition_type_through"."mortgage_condition_id" IS 'Условия';
COMMENT ON COLUMN "mortgage_calсutator_matrix_condition_type_through"."mortgage_payments_types_id" IS 'Статусы';
COMMENT ON TABLE "mortgage_calсutator_matrix_condition_type_through" IS 'Отношения ип матрицы условий к статусам сделок';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "mortgage_calсutator_matrix_condition_type_through";
        DROP TABLE IF EXISTS "mortgage_calculator_condition_matrix";"""