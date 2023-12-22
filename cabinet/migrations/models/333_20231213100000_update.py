from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        alter table "mortgage_calculator_developer_ticket" drop column if exists "ticket_condition_id" cascade;
        alter table "mortgage_calculator_developer_ticket" drop column if exists "ticket_type_id" cascade;
        alter table "mortgage_application_status" drop column if exists "external_code";
        alter table "mortgage_calculator_offer" rename column "payment_per_month" to "monthly_payment";
        alter table "mortgage_calculator_offer" rename column "interest_rate" to "percent_rate";
        alter table "mortgage_calculator_offer" add column if not exists "uid" varchar(255);
        alter table "mortgage_form" alter column "patronymic" drop not null;
        
        create table if not exists "mortgage_application_status_amocrm_statuses_through" (
            "id" serial primary key,
            "mortgage_application_status_id" int references "mortgage_application_status" ("id") on delete cascade,
            "amocrm_status_id" int references "amocrm_statuses" ("id") on delete cascade
        );
        create table if not exists "mortgage_calculator_dev_ticket_offer_through" (
            "id" serial primary key,
            "mortgage_dev_ticket_id" int references "mortgage_calculator_developer_ticket" ("id") on delete cascade,
            "mortgage_offer_id" int references "mortgage_calculator_offer" ("id") on delete cascade
        );
        
        drop table if exists "mortgage_calculator_dev_ticket_proposal_through" cascade;
        drop table if exists "mortgage_submitted_proposal" cascade;
        drop table if exists "mortgage_ticket_types" cascade;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
