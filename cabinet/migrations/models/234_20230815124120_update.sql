-- upgrade --
CREATE TABLE IF NOT EXISTS "users_viewed_property" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "client_id" INT NOT NULL REFERENCES "users_user" ("id") ON DELETE CASCADE,
    "property_id" INT NOT NULL REFERENCES "properties_property" ("id") ON DELETE CASCADE,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "users_viewed_property"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "users_viewed_property"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "users_viewed_property"."client_id" IS 'Пользователь просмотревший квартиру';
COMMENT ON COLUMN "users_viewed_property"."property_id" IS 'Просмотренная квартира';
COMMENT ON TABLE "users_viewed_property" IS 'Модель просмотренных квартир';
-- downgrade --
DROP TABLE IF EXISTS "users_viewed_property";
