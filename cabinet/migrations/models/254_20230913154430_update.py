from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "additional_services_category_type" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(150) NOT NULL
);

INSERT INTO additional_services_category_type (title)
VALUES 
('Возможны без оформления сделки'),
('Необходимо оформить сделку');

ALTER TABLE "additional_services_category" ADD "kind_id" INT DEFAULT 1;
ALTER TABLE "additional_services_category" 
ADD CONSTRAINT "fk_addition_addition_ded55294" 
FOREIGN KEY ("kind_id") REFERENCES "additional_services_category_type" ("id") ON DELETE CASCADE;

ALTER TABLE "additional_services_category" ADD COLUMN IF NOT EXISTS "kind_id" INT REFERENCES "additional_services_category_type" ("id") ON DELETE CASCADE DEFAULT 1;

COMMENT ON COLUMN "additional_services_category_type"."id" IS 'ID';
COMMENT ON COLUMN "additional_services_category_type"."title" IS 'Название';
COMMENT ON TABLE "additional_services_category_type" IS 'Тип категорий (видов) услуг';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "additional_services_category" DROP CONSTRAINT "fk_addition_addition_ded55294";
        ALTER TABLE "additional_services_category" DROP COLUMN "kind_id";
        DROP TABLE IF EXISTS "additional_services_category_type";
        """
