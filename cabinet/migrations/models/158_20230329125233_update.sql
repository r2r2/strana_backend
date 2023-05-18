-- upgrade --
ALTER TABLE "users_interests" ADD "interest_status" SMALLINT;
ALTER TABLE "users_interests" ADD "interest_special_offers" TEXT;
ALTER TABLE "users_interests" ADD "interest_final_price" BIGINT;
ALTER TABLE "properties_property" ADD "special_offers" TEXT;
ALTER TABLE "properties_property" ADD "similar_property_global_id" VARCHAR(200);
-- downgrade --
ALTER TABLE "properties_property" DROP COLUMN "special_offers";
ALTER TABLE "properties_property" DROP COLUMN "similar_property_global_id";
ALTER TABLE "users_interests" DROP COLUMN "interest_status";
ALTER TABLE "users_interests" DROP COLUMN "interest_special_offers";
ALTER TABLE "users_interests" DROP COLUMN "interest_final_price";
