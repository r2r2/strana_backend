from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "additional_services_category" DROP CONSTRAINT "fk_addition_addition_ded55294";
        ALTER TABLE "additional_services_service" ADD "kind_id" INT DEFAULT 1;
        ALTER TABLE "additional_services_category" DROP COLUMN "kind_id";
        DROP TABLE IF EXISTS "additional_services_ticket_statuses";
        ALTER TABLE "additional_services_service" ADD CONSTRAINT "fk_addition_addition_f6752d5b" FOREIGN KEY ("kind_id") REFERENCES "additional_services_category_type" ("id") ON DELETE SET NULL;
        ALTER TABLE additional_services_category_type RENAME TO additional_services_service_type;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE additional_services_service_type RENAME TO additional_services_category_type;
        ALTER TABLE "additional_services_service" DROP CONSTRAINT "fk_addition_addition_f6752d5b";
        ALTER TABLE "additional_services_service" DROP COLUMN "kind_id";
        ALTER TABLE "additional_services_category" ADD "kind_id" INT;
        ALTER TABLE "additional_services_category" ADD CONSTRAINT "fk_addition_addition_ded55294" FOREIGN KEY ("kind_id") REFERENCES "additional_services_category_type" ("id") ON DELETE SET NULL;
        """
