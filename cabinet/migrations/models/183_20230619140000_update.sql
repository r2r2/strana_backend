-- upgrade --
CREATE TABLE IF NOT EXISTS "mainpage_ticket" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "phone" VARCHAR(20) NOT NULL,
    "user_amocrm_id" INT,
    "booking_amocrm_id" INT,
    "note" TEXT,
    "type" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "mainpage_ticket"."phone" IS 'Номер телефона';
COMMENT ON COLUMN "mainpage_ticket"."user_amocrm_id" IS 'ID пользователя в AmoCRM';
COMMENT ON COLUMN "mainpage_ticket"."booking_amocrm_id" IS 'ID брони в AmoCRM';
COMMENT ON COLUMN "mainpage_ticket"."note" IS 'Примечание';
COMMENT ON COLUMN "mainpage_ticket"."created_at" IS 'Время создания';
COMMENT ON COLUMN "mainpage_ticket"."updated_at" IS 'Время последнего обновления';
COMMENT ON TABLE "mainpage_ticket" IS 'Заявка';;
CREATE TABLE "mainpage_ticket_city_through" ("city_id" INT NOT NULL REFERENCES "cities_city" ("id") ON DELETE CASCADE,"ticket_id" INT NOT NULL REFERENCES "mainpage_ticket" ("id") ON DELETE CASCADE);
COMMENT ON TABLE "mainpage_ticket_city_through" IS 'Город';
-- downgrade --
DROP TABLE IF EXISTS "mainpage_ticket_city_through";
DROP TABLE IF EXISTS "mainpage_ticket";
