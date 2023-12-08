from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "mortgage_calculator_banks" ADD COLUMN IF NOT EXISTS "uid" VARCHAR(255) NOT NULL;
        ALTER TABLE "mortgage_calculator_program" ADD COLUMN IF NOT EXISTS "slug" VARCHAR(255) NOT NULL;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "mortgage_calculator_banks" DROP COLUMN IF EXISTS "uid";
        ALTER TABLE "mortgage_calculator_program" DROP COLUMN IF EXISTS "slug";
        """
