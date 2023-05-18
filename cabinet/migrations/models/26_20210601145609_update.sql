-- upgrade --
CREATE TABLE "users_properties_interested" ("user_id" INT NOT NULL REFERENCES "users_user" ("id") ON DELETE CASCADE,"property_id" INT NOT NULL REFERENCES "properties_property" ("id") ON DELETE SET NULL);
-- downgrade --
DROP TABLE IF EXISTS "users_properties_interested";
