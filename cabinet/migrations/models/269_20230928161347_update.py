from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users_consultation_type" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(30) NOT NULL,
    "priority" INT NOT NULL
);
COMMENT ON COLUMN "users_consultation_type"."id" IS 'ID';
COMMENT ON COLUMN "users_consultation_type"."name" IS 'Название';
COMMENT ON COLUMN "users_consultation_type"."priority" IS 'Приоритет';
COMMENT ON TABLE "users_consultation_type" IS 'Справочник типов консультаций';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "users_consultation_type";"""
