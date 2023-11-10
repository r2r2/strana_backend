from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "offers_offer" ALTER COLUMN "updated_at" TYPE TIMESTAMPTZ USING "updated_at"::TIMESTAMPTZ;
        ALTER TABLE "offers_offer" ALTER COLUMN "created_at" SET DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "offers_template" ADD "link" VARCHAR(512);
        ALTER TABLE "offers_template" ADD "site_id" INT;
        ALTER TABLE "offers_template" ADD "page_id" INT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "offers_offer" ALTER COLUMN "updated_at" TYPE TIMESTAMPTZ USING "updated_at"::TIMESTAMPTZ;
        ALTER TABLE "offers_offer" ALTER COLUMN "created_at" SET DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "offers_template" DROP COLUMN "link";
        ALTER TABLE "offers_template" DROP COLUMN "site_id";
        ALTER TABLE "offers_template" DROP COLUMN "page_id";"""
