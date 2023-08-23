-- upgrade --
ALTER TABLE "cities_city" ADD "timezone_offset" INT NOT NULL  DEFAULT 0;
-- downgrade --
ALTER TABLE "cities_city" DROP COLUMN "timezone_offset";
