from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "mortgage_calculator_dev_ticket_to_ticket_through";
        DROP TABLE IF EXISTS "mortgage_calcutator_ticket_booking_through";
        DROP TABLE IF EXISTS "mortgage_calcutator_ticket_to_ticket_type_through";
        DROP TABLE IF EXISTS "mortgage_calculator_ticket" CASCADE;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
