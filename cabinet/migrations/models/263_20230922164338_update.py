from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "additional_services_service" DROP COLUMN "group_status_id";
        ALTER TABLE "additional_services_service" ADD "group_status_id" INT;
        ALTER TABLE "additional_services_service" ADD CONSTRAINT "fk_addition_group_status_fef55294" FOREIGN KEY ("group_status_id") REFERENCES "additional_services_group_statuses" ("id") ON DELETE SET NULL;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "additional_services_service" DROP COLUMN "group_status_id";
        ALTER TABLE "additional_services_category" ADD "group_status_id" INT;
        ALTER TABLE "additional_services_service" ADD CONSTRAINT "fk_addition_addition_f6752d5b" FOREIGN KEY ("group_status_id") REFERENCES "additional_services_group_statuses" ("id") ON DELETE SET NULL;
        """
