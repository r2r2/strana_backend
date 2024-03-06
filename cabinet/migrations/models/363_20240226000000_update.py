from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        create table if not exists mortgage_form(
            id serial primary key,
            booking_id int,
            phone varchar(20),
            surname varchar(100),
            name varchar(100),
            patronymic varchar(100),
            position varchar(100),
            company varchar(100),
            experience varchar(100),
            average_salary varchar(100),
            document_id int,
            created_at timestamp with time zone default now(),
            updated_at timestamp with time zone default now()
        );
        alter table mortgage_form add constraint fk_booking_id foreign key (booking_id) 
        references booking_booking(id) on delete cascade;
        
        create table if not exists ddu_contract(
            id serial primary key,
            number varchar(100),
            contract_date date,
            reference_file varchar(2000),
            created_at timestamp with time zone default now(),
            updated_at timestamp with time zone default now(),
            status varchar(100)
        );
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        drop table if exists mortgage_form cascade;
        drop table if exists ddu_contract cascade;
"""