from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "additional_services_ticket" ADD "user_id" INT;
        ALTER TABLE "additional_services_ticket" ADD CONSTRAINT "fk_addition_users_us_da5c06a7" FOREIGN KEY ("user_id") REFERENCES "users_user" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "additional_services_ticket" DROP CONSTRAINT "fk_addition_users_us_da5c06a7";
        ALTER TABLE "additional_services_ticket" DROP COLUMN "user_id";"""
