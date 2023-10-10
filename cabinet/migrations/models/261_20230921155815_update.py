from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "additional_services_group_statuses" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(150),
    "slug" VARCHAR(50)  UNIQUE,
    "sort" INT NOT NULL  DEFAULT 0
);
ALTER TABLE "amocrm_statuses" ADD "add_service_group_status_id" INT;
COMMENT ON COLUMN "additional_services_group_statuses"."id" IS 'ID';
COMMENT ON COLUMN "additional_services_group_statuses"."name" IS 'Название';
COMMENT ON COLUMN "additional_services_group_statuses"."slug" IS 'slug';
COMMENT ON COLUMN "additional_services_group_statuses"."sort" IS 'Приоритет';
COMMENT ON TABLE "additional_services_group_statuses" IS 'Модель группирующих статусов для доп услуг';
ALTER TABLE "amocrm_statuses" ADD CONSTRAINT "fk_amocrm_s_addition_ae9b1939" FOREIGN KEY ("add_service_group_status_id") REFERENCES "additional_services_group_statuses" ("id") ON DELETE SET NULL;
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "amocrm_statuses" DROP CONSTRAINT "fk_amocrm_s_addition_ae9b1939";
        ALTER TABLE "amocrm_statuses" DROP COLUMN "add_service_group_status_id";
        DROP TABLE IF EXISTS "additional_services_group_statuses";"""
