-- upgrade --
CREATE TABLE IF NOT EXISTS "booking_booking" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "bank_id" UUID,
    "until" TIMESTAMPTZ,
    "created" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "active" BOOL NOT NULL  DEFAULT True,
    "contract_accepted" BOOL NOT NULL  DEFAULT False,
    "personal_filled" BOOL NOT NULL  DEFAULT False,
    "phone_submitted" BOOL NOT NULL  DEFAULT False,
    "params_checked" BOOL NOT NULL  DEFAULT False,
    "price_payed" BOOL NOT NULL  DEFAULT False,
    "currency" INT NOT NULL  DEFAULT 643,
    "order_number" UUID NOT NULL,
    "amount" DECIMAL(15,2),
    "payment_url" VARCHAR(350),
    "amocrm_id" BIGINT,
    "stage" VARCHAR(100),
    "substage" VARCHAR(100),
    "project_id" INT REFERENCES "projects_project" ("id") ON DELETE CASCADE,
    "building_id" INT REFERENCES "buildings_building" ("id") ON DELETE CASCADE,
    "user_id" INT REFERENCES "users_user" ("id") ON DELETE CASCADE,
    "property_id" INT REFERENCES "properties_property" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "booking_booking"."id" IS 'ID';
COMMENT ON COLUMN "booking_booking"."bank_id" IS 'ID Банка';
COMMENT ON COLUMN "booking_booking"."until" IS 'Забронировано до';
COMMENT ON COLUMN "booking_booking"."created" IS 'Создано';
COMMENT ON COLUMN "booking_booking"."active" IS 'Активно';
COMMENT ON COLUMN "booking_booking"."contract_accepted" IS 'Договор принят';
COMMENT ON COLUMN "booking_booking"."personal_filled" IS 'Персональные данные заполнены';
COMMENT ON COLUMN "booking_booking"."phone_submitted" IS 'Телефон подтвержден';
COMMENT ON COLUMN "booking_booking"."params_checked" IS 'Параметры проверены';
COMMENT ON COLUMN "booking_booking"."price_payed" IS 'Стоиомсть оплачена';
COMMENT ON COLUMN "booking_booking"."currency" IS 'Валюта';
COMMENT ON COLUMN "booking_booking"."order_number" IS 'Номер заказа';
COMMENT ON COLUMN "booking_booking"."amount" IS 'Стоимость';
COMMENT ON COLUMN "booking_booking"."payment_url" IS 'Ссылка на оплату';
COMMENT ON COLUMN "booking_booking"."amocrm_id" IS 'ID в AmoCRM';
COMMENT ON COLUMN "booking_booking"."stage" IS 'Этап';
COMMENT ON COLUMN "booking_booking"."substage" IS 'Подэтап';
COMMENT ON COLUMN "booking_booking"."project_id" IS 'Проект';
COMMENT ON COLUMN "booking_booking"."building_id" IS 'Корпус';
COMMENT ON COLUMN "booking_booking"."user_id" IS 'Пользователь';
COMMENT ON COLUMN "booking_booking"."property_id" IS 'Объект недвижимости';
COMMENT ON TABLE "booking_booking" IS 'Бронирование';
-- downgrade --
DROP TABLE IF EXISTS "booking_booking";
