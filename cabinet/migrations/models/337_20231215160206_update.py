from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE UNIQUE INDEX "uid_users_user_role_id_a457e4" ON "users_user" ("role_id", "phone");
        CREATE UNIQUE INDEX "uid_users_user_role_id_6c627e" ON "users_user" ("role_id", "amocrm_id");
        CREATE UNIQUE INDEX "uid_users_user_role_id_e4c016" ON "users_user" ("role_id", "email");
        CREATE UNIQUE INDEX "uid_users_user_role_id_bee3c9" ON "users_user" ("role_id", "username");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "uid_users_user_role_id_bee3c9";
        DROP INDEX "uid_users_user_role_id_e4c016";
        DROP INDEX "uid_users_user_role_id_6c627e";
        DROP INDEX "uid_users_user_role_id_a457e4";"""
