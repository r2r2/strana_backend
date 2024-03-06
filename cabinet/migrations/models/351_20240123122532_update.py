from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "privilege_program" DROP COLUMN "until";
        ALTER TABLE "privilege_program" ADD "until" TIMESTAMPTZ;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "privilege_program" DROP COLUMN "until";
        ALTER TABLE "privilege_program" ADD "until" DOUBLE PRECISION;"""
