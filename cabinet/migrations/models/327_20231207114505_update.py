from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "mortgage_calculator_condition_matrix" ADD "name" VARCHAR(100) NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "mortgage_calculator_condition_matrix" DROP COLUMN "name";"""
