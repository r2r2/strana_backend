-- upgrade --
ALTER TABLE "cities_city" ADD "phone" VARCHAR(20);
-- downgrade --
ALTER TABLE "cities_city" DROP COLUMN "phone";
