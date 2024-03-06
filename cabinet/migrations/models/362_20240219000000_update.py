from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        drop table if exists mortgage_form cascade;
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
    create table mortgage_form (
        id serial primary key,
        created_at timestamp with time zone default now(),
        updated_at timestamp with time zone default now(),
        deleted_at timestamp with time zone
    );
"""