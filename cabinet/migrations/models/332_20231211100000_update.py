from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        drop table if exists "mortgage_calculator_ticket_status_through";
        drop table if exists "mortgage_canlutator_offer_bank_through";
        drop table if exists "mortgage_canlutator_offer_program_through";
        drop table if exists "mortgage_canlutator_submitted_proposal_offer_through";
        
        alter table "mortgage_calсutator_condition_program_through" rename to "mortgage_calculator_condition_program_through";
        alter table "mortgage_calсutator_condition_bank_through" rename to "mortgage_calculator_condition_bank_through";
        alter table "mortgage_calcutator_condition" rename to "mortgage_calculator_condition";
        alter table "mortgage_calсutator_matrix_amocrm_statuses_through" rename to "mortgage_calсulator_matrix_amocrm_statuses_through";
        
        alter table "mortgage_calculator_developer_ticket" add column if not exists "calculator_condition_id" int references "mortgage_calculator_condition" ("id") on delete cascade;
        alter table "mortgage_calculator_developer_ticket" add column if not exists "ticket_condition_id" int references "mortgage_calculator_condition_matrix" ("id") on delete cascade;
        alter table "mortgage_calculator_developer_ticket" add column if not exists "form_data_id" int references "mortgage_form" ("id") on delete cascade;
        alter table "mortgage_calculator_developer_ticket" add column if not exists "status_id" int references "mortgage_application_status" ("id") on delete cascade;
        alter table "mortgage_submitted_proposal" drop column if exists "mortgage_application";
        alter table "mortgage_submitted_proposal" add column if not exists "mortgage_offer_id" int references "mortgage_calculator_offer" ("id") on delete cascade;
        alter table "mortgage_submitted_proposal" alter column "name" type varchar(255);
        alter table "mortgage_submitted_proposal" alter column "external_code" type varchar(255);
        alter table "mortgage_calculator_offer" rename column "offer_name" to "name";
        alter table "mortgage_calculator_offer" alter column "name" type varchar(255);
        alter table "mortgage_application_status" rename column "status_name" to "name";
        alter table "mortgage_application_status" alter column "name" type varchar(255);
        alter table "mortgage_calculator_offer" add column if not exists "bank_id" int references "mortgage_calculator_banks" ("id") on delete cascade;
        alter table "mortgage_calculator_offer" add column if not exists "program_id" int references "mortgage_calculator_program" ("id") on delete cascade;
        alter table "mortgage_calculator_program" rename column "program_name" to "name";
        alter table "mortgage_calculator_program" alter column "name" type varchar(255);
        alter table "mortgage_calculator_banks" rename column "bank_name" to "name";
        alter table "mortgage_calculator_banks" alter column "name" type varchar(255);
        alter table "mortgage_calculator_banks" rename column "bank_icon" to "icon";
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
