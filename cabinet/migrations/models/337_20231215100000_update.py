from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        create table if not exists "mortgage_calculator_text_blocks"(
            id serial primary key,
            title text,
            text text,
            slug varchar(100) not null unique,
            lk_type varchar(10),
            description text,
            created_at timestamp with time zone default now(),
            updated_at timestamp with time zone default now()
        );
        create table if not exists "mortgage_calculator_text_block_city_through"(
            id serial primary key,
            mortgage_text_block_id int references "mortgage_calculator_text_blocks" (id) on delete cascade,
            city_id int references "cities_city" (id) on delete cascade
        );
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        drop table if exists "mortgage_calculator_text_block_city_through" cascade;
        drop table if exists "mortgage_calculator_text_blocks" cascade;
        """
