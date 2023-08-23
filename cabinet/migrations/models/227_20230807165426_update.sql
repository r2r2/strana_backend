-- upgrade --
ALTER TABLE "agencies_agency" DROP CONSTRAINT IF EXISTS "fk_agencies_cities_c_afe0d7c7";
ALTER TABLE "agencies_agency" DROP COLUMN IF EXISTS "city_id";
ALTER TABLE "agencies_agency"
    ADD COLUMN IF NOT EXISTS "city" VARCHAR (30) DEFAULT 'city';
-- downgrade --
