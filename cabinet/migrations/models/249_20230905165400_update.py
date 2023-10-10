from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_checks" ADD "button_pressed" BOOL NOT NULL  DEFAULT False;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_checks" DROP COLUMN "button_pressed";
    """
