-- upgrade --
ALTER TABLE "agencies_agency" ADD "city_id" INT;
CREATE TABLE "users_cities" (
    "city_id" INT NOT NULL REFERENCES "cities_city" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users_user" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "users_cities" IS 'Пользователи';
ALTER TABLE "agencies_agency" ADD CONSTRAINT "fk_agencies_cities_c_74ef1a5f" FOREIGN KEY ("city_id") REFERENCES "cities_city" ("id") ON DELETE CASCADE;
UPDATE agencies_agency
SET city_id = (
    SELECT cities_city.id
    FROM cities_city
    WHERE cities_city.name = agencies_agency.city
);
COMMENT ON COLUMN "agencies_agency"."city_id" IS 'Город агентства';;
-- downgrade --
ALTER TABLE "agencies_agency" DROP CONSTRAINT "fk_agencies_cities_c_74ef1a5f";
ALTER TABLE "agencies_agency" DROP COLUMN "city_id";
DROP TABLE IF EXISTS "users_cities";
