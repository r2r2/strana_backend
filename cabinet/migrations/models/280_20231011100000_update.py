from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    alter table event_list alter column event_date type timestamptz;
    """
