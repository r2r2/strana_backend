from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    UPDATE properties_property
    SET type = UPPER(type)
    WHERE type IN ('flat', 'parking', 'commercial', 'pantry', 'commercial_apartment');
"""


