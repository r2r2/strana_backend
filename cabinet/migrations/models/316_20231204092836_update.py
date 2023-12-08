from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "mortage_calculator_offers_program_through";
        DROP TABLE IF EXISTS "mortage_calculator_offers_banks_through";
        DROP TABLE IF EXISTS "mortage_calculator_offer";
        DROP TABLE IF EXISTS "mortage_calculator_banks";
        DROP TABLE IF EXISTS "mortage_calculator_program";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
"""
