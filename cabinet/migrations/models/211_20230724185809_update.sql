
-- upgrade --
CREATE TABLE IF NOT EXISTS "cities_iplocation" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "ip_address" VARCHAR(15) NOT NULL,
    "city_id" INT REFERENCES "cities_city" ("id") ON DELETE CASCADE,
    "updated_at" TIMESTAMPTZ
);
-- downgrade --
DROP TABLE IF EXISTS "cities_iplocation";
