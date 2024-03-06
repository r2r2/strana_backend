from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_strana_office_admin" ADD "responsible_kc" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "users_strana_office_admin" ALTER COLUMN "project_id" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_strana_office_admin" DROP COLUMN "responsible_kc";
        ALTER TABLE "users_strana_office_admin" ALTER COLUMN "project_id" SET NOT NULL;"""
