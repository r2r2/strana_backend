from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        INSERT INTO offers_offer_source (name, slug)
        VALUES ('Панель менеджера', 'panel_manager');"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DELETE FROM offers_offer_source
        WHERE slug = 'panel_manager';
        ;"""
