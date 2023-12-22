from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "mortgage_calculator_condition_matrix" DROP COLUMN IF EXISTS "is_apply_for_mortgage";
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "mortgage_calculator_condition_matrix" ADD COLUMN IF NOT EXISTS "is_apply_for_mortgage" VARCHAR(50) NOT NULL;
        """
