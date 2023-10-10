from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_fixing_conditions_matrix" ADD "priority" INT NOT NULL  DEFAULT 0;
        ALTER TABLE "booking_fixing_conditions_matrix" ADD "consultation_type_id" INT;
        ALTER TABLE "booking_fixing_conditions_matrix" ADD "amo_responsible_user_id" VARCHAR(200);
        CREATE TABLE IF NOT EXISTS "booking_fixing_conditions_matrix_pipeline_through" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "booking_fixing_conditions_matrix_id" INT NOT NULL REFERENCES "booking_fixing_conditions_matrix" ("id") ON DELETE CASCADE,
    "pipeline_id" INT NOT NULL REFERENCES "amocrm_pipelines" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_booking_fix_pipelin_369499" UNIQUE ("pipeline_id", "booking_fixing_conditions_matrix_id")
);
COMMENT ON TABLE "booking_fixing_conditions_matrix_pipeline_through" IS 'Воронки';
COMMENT ON COLUMN "booking_fixing_conditions_matrix"."priority" IS 'Приоритет';
COMMENT ON COLUMN "booking_fixing_conditions_matrix"."consultation_type_id" IS 'Тип консультации';
ALTER TABLE "booking_fixing_conditions_matrix" ADD CONSTRAINT 
"fk_booking__users_co_5fc0857f" FOREIGN KEY ("consultation_type_id") REFERENCES "users_consultation_type" ("id") ON DELETE SET NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_fixing_conditions_matrix" DROP CONSTRAINT "fk_booking__users_co_5fc0857f";
        DROP TABLE IF EXISTS "booking_fixing_conditions_matrix_pipeline_through";
        ALTER TABLE "booking_fixing_conditions_matrix" DROP COLUMN "priority";
        ALTER TABLE "booking_fixing_conditions_matrix" DROP COLUMN "consultation_type_id";
        ALTER TABLE "booking_fixing_conditions_matrix" DROP COLUMN "amo_responsible_user_id";"""
