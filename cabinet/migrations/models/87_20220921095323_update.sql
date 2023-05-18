-- upgrade --
ALTER TABLE "properties_property" ADD "final_price" BIGINT;
-- downgrade --
ALTER TABLE "properties_property" DROP COLUMN "final_price";
