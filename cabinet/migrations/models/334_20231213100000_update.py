from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        alter table "mortgage_calculator_condition" alter column "proof_of_income" drop not null;        
        alter table "mortgage_calculator_offer" alter column "external_code" drop not null;        
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
