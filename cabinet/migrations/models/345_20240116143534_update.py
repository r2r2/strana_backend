from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "privilege_request" ADD "user_id" INT;
        ALTER TABLE "privilege_request" ADD CONSTRAINT "fk_privileg_users_us_a4e265bf" FOREIGN KEY ("user_id") REFERENCES "users_user" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "privilege_request" DROP CONSTRAINT "fk_privileg_users_us_a4e265bf";
        ALTER TABLE "privilege_request" DROP COLUMN "user_id";"""
