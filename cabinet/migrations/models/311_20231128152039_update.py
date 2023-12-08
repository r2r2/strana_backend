from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_checks" ADD "project_id" INT;
        ALTER TABLE "users_checks" ADD CONSTRAINT "fk_users_ch_projects_9f44e372" FOREIGN KEY ("project_id") REFERENCES "projects_project" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_checks" DROP CONSTRAINT "fk_users_ch_projects_9f44e372";
        ALTER TABLE "users_checks" DROP COLUMN "project_id";"""
