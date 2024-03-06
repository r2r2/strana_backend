from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        alter table mortgage_form rename to personal_information;
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        alter table personal_information rename to mortgage_form;
"""