from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "additional_services_service" DROP COLUMN "group_status_id";
        ALTER TABLE "additional_services_ticket" DROP COLUMN "status_id";
        ALTER TABLE "additional_services_ticket" ADD "group_status_id" INT;
        ALTER TABLE "additional_services_ticket" ADD CONSTRAINT "fk_addition_addition_140cfcc2" FOREIGN KEY ("group_status_id") REFERENCES "additional_services_group_statuses" ("id") ON DELETE SET NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "additional_services_ticket" DROP CONSTRAINT "fk_addition_addition_140cfcc2";
        ALTER TABLE "additional_services_service" ADD "group_status_id" INT;
        ALTER TABLE "additional_services_ticket" DROP COLUMN "group_status_id";
        ALTER TABLE "additional_services_ticket" ADD "status_id" INT;
        ALTER TABLE "additional_services_service" ADD CONSTRAINT "fk_addition_addition_84776db9" FOREIGN KEY ("group_status_id") REFERENCES "additional_services_group_statuses" ("id") ON DELETE SET NULL;
        ALTER TABLE "additional_services_ticket" ADD CONSTRAINT "fk_addition_amocrm_s_0863f198" FOREIGN KEY ("status_id") REFERENCES "amocrm_statuses" ("id") ON DELETE SET NULL;"""
