from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "event_list" ADD COLUMN IF NOT EXISTS "text" TEXT DEFAULT 
        'QR-код активен 1 раз после прохода, пересылка третьим лицам запрещена';
        ;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "event_list" DROP COLUMN IF EXISTS "text";"""
