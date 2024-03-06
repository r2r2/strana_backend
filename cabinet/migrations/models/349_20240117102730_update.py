from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_strana_office_admin" ADD "type" VARCHAR(20) NOT NULL  DEFAULT 'kc';
        ALTER TABLE "users_strana_office_admin" DROP COLUMN "responsible_kc";
        ALTER TABLE "users_strana_office_admin" DROP COLUMN "project_id";
        CREATE TABLE "users_strana_office_admins_project_through" (
    "strana_office_admin_id" INT NOT NULL REFERENCES "users_strana_office_admin" ("id") ON DELETE CASCADE,
    "project_id" INT NOT NULL REFERENCES "projects_project" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "users_strana_office_admins_project_through";
        ALTER TABLE "users_strana_office_admin" ADD "responsible_kc" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "users_strana_office_admin" ADD "project_id" INT;
        ALTER TABLE "users_strana_office_admin" DROP COLUMN "type";
        ALTER TABLE "users_strana_office_admin" ADD CONSTRAINT "fk_users_st_projects_571e6ff3" FOREIGN KEY ("project_id") REFERENCES "projects_project" ("id") ON DELETE CASCADE;"""
