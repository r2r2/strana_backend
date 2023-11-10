from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """        
        ALTER TABLE "payments_property_price" ADD "property_id" INT;
        ALTER TABLE "payments_property_price" ADD CONSTRAINT "fk_payments_properti_fdc8bbd0" FOREIGN KEY ("property_id") REFERENCES "properties_property" ("id") ON DELETE CASCADE;
        
        ALTER TABLE "payments_price_offer_matrix" ADD "mortgage_type_id" INT;
        ALTER TABLE "payments_price_offer_matrix" ADD CONSTRAINT "fk_payments_payments_d3d8d356" FOREIGN KEY ("mortgage_type_id") REFERENCES "payments_mortgage_types" ("id") ON DELETE CASCADE;
        ALTER TABLE "payments_price_offer_matrix" DROP CONSTRAINT "fk_payments_payments_4a4bdc6d";
        CREATE UNIQUE INDEX "uid_payments_pr_price_t_9081da" ON "payments_price_offer_matrix" ("price_type_id");
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "payments_property_price" DROP CONSTRAINT "fk_payments_properti_fdc8bbd0";
        ALTER TABLE "payments_property_price" DROP COLUMN "property_id";
        
        ALTER TABLE "payments_price_offer_matrix" DROP CONSTRAINT "fk_payments_payments_d3d8d356";
        ALTER TABLE "payments_price_offer_matrix" DROP COLUMN "mortgage_type_id";
        DROP INDEX "uid_payments_pr_price_t_9081da";
        ALTER TABLE "payments_price_offer_matrix" ADD CONSTRAINT "fk_payments_payments_4a4bdc6d" FOREIGN KEY ("price_type_id") REFERENCES "payments_property_price_type" ("id") ON DELETE CASCADE;
        """
