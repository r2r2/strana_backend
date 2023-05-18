-- upgrade --
CREATE TABLE IF NOT EXISTS "booking_history" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at_online_purchase_step" VARCHAR(32) NOT NULL,
    "documents" JSONB NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "message" VARCHAR(1000) NOT NULL,
    "booking_id" INT NOT NULL REFERENCES "booking_booking" ("id") ON DELETE CASCADE,
    "property_id" INT NOT NULL REFERENCES "properties_property" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users_user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "booking_history"."id" IS 'ID';
COMMENT ON COLUMN "booking_history"."created_at_online_purchase_step" IS 'Стадия онлайн-покупки сделки на момент создания записи';
COMMENT ON COLUMN "booking_history"."documents" IS 'Прикреплённые документы';
COMMENT ON COLUMN "booking_history"."created_at" IS 'Дата и время создания';
COMMENT ON COLUMN "booking_history"."message" IS 'Описание';
COMMENT ON COLUMN "booking_history"."booking_id" IS 'Сделка';
COMMENT ON COLUMN "booking_history"."property_id" IS 'Собственность';
COMMENT ON COLUMN "booking_history"."user_id" IS 'Сделка';
COMMENT ON TABLE "booking_history" IS 'Конкретная запись из истории сделки';;
-- downgrade --
DROP TABLE IF EXISTS "booking_history";
