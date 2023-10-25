from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_user" ADD "is_ready_for_authorisation_by_superuser" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "users_user" ADD "can_login_as_another_user" BOOL NOT NULL  DEFAULT False;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_user" DROP COLUMN "is_ready_for_authorisation_by_superuser";
        ALTER TABLE "users_user" DROP COLUMN "can_login_as_another_user";
        """
