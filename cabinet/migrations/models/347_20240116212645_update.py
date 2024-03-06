from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE INDEX "idx_historical__client__9b6c0f" ON "historical_dispute_data" ("client_id");
        CREATE INDEX "idx_users_userl_user_id_6ab0e8" ON "users_userlog" ("user_id");
        CREATE INDEX "idx_booking_boo_user_id_82c55d" ON "booking_booking" ("user_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_historical__client__9b6c0f";
        DROP INDEX "idx_users_userl_user_id_6ab0e8";
        DROP INDEX "idx_booking_boo_user_id_82c55d";"""
