-- upgrade --
CREATE TABLE IF NOT EXISTS "users_cities" (
    "city_id" INT NOT NULL REFERENCES "cities_city" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users_user" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "users_cities";