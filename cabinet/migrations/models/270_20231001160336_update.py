from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "main_page_manager" ADD "lastname" VARCHAR(100);
        ALTER TABLE "main_page_manager" ADD "name" VARCHAR(100);
        ALTER TABLE "main_page_manager" ADD "work_schedule" VARCHAR(512);
        ALTER TABLE "main_page_manager" ADD "email" VARCHAR(100);
        ALTER TABLE "main_page_manager" ADD "phone" VARCHAR(20);
        ALTER TABLE "main_page_manager" ADD "patronymic" VARCHAR(100);
        ALTER TABLE "main_page_manager" DROP COLUMN "manager_id";
        ALTER TABLE "main_page_content" ALTER COLUMN "title" DROP NOT NULL;
        ALTER TABLE "main_page_content" ALTER COLUMN "comment" DROP NOT NULL;
        ALTER TABLE "main_page_content" ALTER COLUMN "text" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "main_page_content" ALTER COLUMN "title" SET NOT NULL;
        ALTER TABLE "main_page_content" ALTER COLUMN "comment" SET NOT NULL;
        ALTER TABLE "main_page_content" ALTER COLUMN "text" SET NOT NULL;
        ALTER TABLE "main_page_manager" ADD "manager_id" BIGINT NOT NULL;
        ALTER TABLE "main_page_manager" DROP COLUMN "lastname";
        ALTER TABLE "main_page_manager" DROP COLUMN "name";
        ALTER TABLE "main_page_manager" DROP COLUMN "work_schedule";
        ALTER TABLE "main_page_manager" DROP COLUMN "email";
        ALTER TABLE "main_page_manager" DROP COLUMN "phone";
        ALTER TABLE "main_page_manager" DROP COLUMN "patronymic";"""
