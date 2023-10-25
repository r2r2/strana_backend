from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_user" ADD "is_offer_accepted" BOOL NOT NULL  DEFAULT False;
COMMENT ON COLUMN "users_user"."is_offer_accepted" IS 'Была ли оферта принята';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_user" DROP COLUMN "is_offer_accepted";"""
