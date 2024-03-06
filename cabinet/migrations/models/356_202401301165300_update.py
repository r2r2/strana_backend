from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE INDEX "users_cities_city_t_9081da" ON "users_cities" ("city_id");
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "users_cities_city_t_9081da";
        """
