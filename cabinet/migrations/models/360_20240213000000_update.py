from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        drop table if exists "mortgage_application_status_amocrm_statuses_through" cascade;
        drop table if exists "mortgage_application_status" cascade;
        drop table if exists "mortgage_calculator_banks" cascade;
        drop table if exists "mortgage_calculator_condition_program_through" cascade;
        drop table if exists "mortgage_calculator_condition_bank_through" cascade;
        drop table if exists "mortgage_calculator_condition" cascade;
        drop table if exists "mortgage_calсulator_matrix_amocrm_statuses_through" cascade;
        drop table if exists "mortgage_calculator_condition_matrix" cascade;
        drop table if exists "mortgage_calculator_dev_ticket_offer_through" cascade;
        drop table if exists "mortgage_calculator_developer_ticket" cascade;
        drop table if exists "mortgage_calculator_offer" cascade;
        drop table if exists "mortgage_calculator_program" cascade;
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        select 1 from booking_booking limit 1; """
