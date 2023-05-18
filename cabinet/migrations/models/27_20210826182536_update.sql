-- upgrade --
ALTER TABLE "showtimes_showtime" ADD "property_type" VARCHAR(50);
ALTER TABLE "showtimes_showtime" ADD "amocrm_id" BIGINT;
-- downgrade --
ALTER TABLE "showtimes_showtime" DROP COLUMN "property_type";
ALTER TABLE "showtimes_showtime" DROP COLUMN "amocrm_id";
