from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE INDEX "idx_users_confi_client__4f85f3" ON "users_confirm_client_assign" ("client_id");
        CREATE INDEX "idx_users_user_role_id_d2daed" ON "users_user" ("role_id");
        CREATE INDEX "idx_users_user_type_be413f" ON "users_user" ("type"); 
        CREATE INDEX "idx_task_manage_booking_78e7b8" ON "task_management_logs" ("booking_id");
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_users_confi_client__4f85f3";
        DROP INDEX "idx_task_manage_booking_78e7b8";
        DROP INDEX "idx_users_user_type_be413f";
        DROP INDEX "idx_users_user_role_id_d2daed";
       """
