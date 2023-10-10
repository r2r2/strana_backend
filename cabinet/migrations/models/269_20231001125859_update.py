from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE UNIQUE INDEX "uid_main_page_c_slug_50ac2f" ON "main_page_content" ("slug");
        ALTER TABLE "main_page_content" ALTER COLUMN "text" DROP NOT NULL;
        ALTER TABLE "main_page_content" ADD "title" TEXT;
        ALTER TABLE "main_page_content" ALTER COLUMN "comment" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_main_page_c_slug_50ac2f";
        ALTER TABLE "main_page_content" ALTER COLUMN "text" SET NOT NULL;
        ALTER TABLE "main_page_content" DROP COLUMN "title";
        ALTER TABLE "main_page_content" ALTER COLUMN "comment" SET NOT NULL;"""
