from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
alter table "mortgage_form" add column if not exists "position" varchar(100) null;
alter table "mortgage_form" add column if not exists "company" varchar(100) null;
alter table "mortgage_form" add column if not exists "experience" varchar(100) null;
alter table "mortgage_form" add column if not exists "average_salary" varchar(100) null;
alter table "mortgage_form" add column if not exists "co_borrowers" text null;
alter table "mortgage_form" add column if not exists "booking_id" int null references "booking_booking" ("id") on delete cascade;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
alter table "mortgage_form" drop column if exists "position";
alter table "mortgage_form" drop column if exists "company";
alter table "mortgage_form" drop column if exists "experience";
alter table "mortgage_form" drop column if exists "average_salary";
alter table "mortgage_form" drop column if exists "co_borrowers";
alter table "mortgage_form" drop column if exists "booking_id";
        """
