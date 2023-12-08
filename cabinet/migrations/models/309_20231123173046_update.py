from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "notifications_rop_emails_dispute" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "fio" VARCHAR(100) NOT NULL,
    "email" VARCHAR(100) NOT NULL,
    "project_id" INT NOT NULL REFERENCES "projects_project" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "notifications_rop_emails_dispute"."id" IS 'ID';
COMMENT ON COLUMN "notifications_rop_emails_dispute"."fio" IS 'ФИО админа';
COMMENT ON COLUMN "notifications_rop_emails_dispute"."email" IS 'Email';
COMMENT ON COLUMN "notifications_rop_emails_dispute"."project_id" IS 'Проект';
COMMENT ON TABLE "notifications_rop_emails_dispute" IS 'Таблица с почтами Руководителей отдела продаж, не путать с юзерами типа роп';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "notifications_rop_emails_dispute";"""
