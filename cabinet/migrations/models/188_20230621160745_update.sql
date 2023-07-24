-- upgrade --
ALTER TABLE "agencies_agency" DROP COLUMN "city";
ALTER TABLE "agencies_agency" DROP CONSTRAINT "fk_agencies_cities_c_74ef1a5f";
ALTER TABLE "agencies_agency" ADD CONSTRAINT "fk_agencies_cities_c_afe0d7c7" FOREIGN KEY ("city_id") REFERENCES "cities_city" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "agencies_agency" DROP CONSTRAINT "fk_agencies_cities_c_afe0d7c7";
ALTER TABLE "agencies_agency" ADD "city" VARCHAR(30) DEFAULT 'city';
ALTER TABLE "agencies_agency" ADD CONSTRAINT "fk_agencies_cities_c_74ef1a5f" FOREIGN KEY ("city_id") REFERENCES "cities_city" ("id") ON DELETE CASCADE;
