from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "mortgage_calculator_matrix_condition_type_through";
        CREATE TABLE IF NOT EXISTS "mortgage_calсutator_matrix_amocrm_statuses_through" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "amocrm_status_id" INT NOT NULL REFERENCES "amocrm_statuses" ("id") ON DELETE CASCADE,
            "mortgage_matrix_condition_id" INT NOT NULL REFERENCES "mortgage_calculator_condition_matrix" ("id") ON DELETE CASCADE
        );
        COMMENT ON COLUMN "mortgage_calсutator_matrix_amocrm_statuses_through"."id" IS 'ID';
        COMMENT ON COLUMN "mortgage_calсutator_matrix_amocrm_statuses_through"."amocrm_status_id" IS 'Статусы сделок';
        COMMENT ON COLUMN "mortgage_calсutator_matrix_amocrm_statuses_through"."mortgage_matrix_condition_id" IS 'Условия';
        COMMENT ON TABLE "mortgage_calсutator_matrix_amocrm_statuses_through" IS 'Промежуточная таблица матрицы условий к статусам сделок.';
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "mortgage_calсutator_matrix_amocrm_statuses_through";
        """
