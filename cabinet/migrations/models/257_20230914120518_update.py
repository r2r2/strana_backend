from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_user" ADD "loyalty_point_amount" INT;
        ALTER TABLE "users_user" ADD "loyalty_status_name" VARCHAR(100);
        ALTER TABLE "users_user" ADD "loyalty_status_icon" VARCHAR(300);
        ALTER TABLE "users_user" ADD "loyalty_status_substrate_card" VARCHAR(300);
        ALTER TABLE "users_user" ADD "loyalty_status_icon_profile" VARCHAR(300);
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_user" DROP COLUMN IF EXISTS "loyalty_point_amount";
        ALTER TABLE "users_user" DROP COLUMN IF EXISTS "loyalty_status_name";
        ALTER TABLE "users_user" DROP COLUMN IF EXISTS "loyalty_status_icon";
        ALTER TABLE "users_user" DROP COLUMN IF EXISTS "loyalty_status_substrate_card";
        ALTER TABLE "users_user" DROP COLUMN IF EXISTS "loyalty_status_icon_profile";
        """
