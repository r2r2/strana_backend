from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users_strana_office_admin" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "fio" VARCHAR(100) NOT NULL,
    "email" VARCHAR(100) NOT NULL,
    "project_id" INT NOT NULL REFERENCES "projects_project" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "users_strana_office_admin"."id" IS 'ID';
COMMENT ON COLUMN "users_strana_office_admin"."fio" IS 'ФИО админа';
COMMENT ON COLUMN "users_strana_office_admin"."email" IS 'Email';
COMMENT ON COLUMN "users_strana_office_admin"."project_id" IS 'Проект';
COMMENT ON TABLE "users_strana_office_admin" IS 'Администратор офиса \"Страна\"';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "users_strana_office_admin";"""
