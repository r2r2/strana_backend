from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "uid_payments_pr_price_t_9081da";
        ALTER TABLE "payments_price_offer_matrix" ALTER COLUMN "price_type_id" DROP NOT NULL;
        ALTER TABLE "payments_price_offer_matrix" ALTER COLUMN "payment_method_id" DROP NOT NULL;
        ALTER TABLE "payments_price_offer_matrix" ADD CONSTRAINT "fk_payments_payments_4a4bdc6d" FOREIGN KEY ("price_type_id") REFERENCES "payments_property_price_type" ("id") ON DELETE SET NULL;
        ALTER TABLE "payments_price_offer_matrix" ADD "default" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "payments_price_offer_matrix" DROP COLUMN "by_dev";
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "payments_price_offer_matrix" DROP CONSTRAINT "fk_payments_payments_4a4bdc6d";
        CREATE UNIQUE INDEX "uid_payments_pr_price_t_9081da" ON "payments_price_offer_matrix" ("price_type_id");
        ALTER TABLE "payments_price_offer_matrix" ADD "by_dev" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "payments_price_offer_matrix" DROP COLUMN "default";
        """
