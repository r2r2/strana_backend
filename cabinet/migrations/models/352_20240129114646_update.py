from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "faq_faq" ADD "page_type_id" VARCHAR(250);
        CREATE TABLE IF NOT EXISTS "faq_faqpagetype" (
    "slug" VARCHAR(250) NOT NULL  PRIMARY KEY,
    "title" VARCHAR(250) NOT NULL
);
COMMENT ON COLUMN "faq_faq"."page_type_id" IS 'Тип страницы';
COMMENT ON COLUMN "faq_faqpagetype"."slug" IS 'Слаг';
COMMENT ON COLUMN "faq_faqpagetype"."title" IS 'Название';
COMMENT ON TABLE "faq_faqpagetype" IS 'Тип страниц для вывода FAQ';
        ALTER TABLE "faq_faq" ADD CONSTRAINT "fk_faq_faq_faq_faqp_59c85692" FOREIGN KEY ("page_type_id") REFERENCES "faq_faqpagetype" ("slug") ON DELETE SET NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "faq_faq" DROP CONSTRAINT "fk_faq_faq_faq_faqp_59c85692";
        ALTER TABLE "faq_faq" DROP COLUMN "page_type_id";
        DROP TABLE IF EXISTS "faq_faqpagetype";"""
