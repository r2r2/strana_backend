-- upgrade --
CREATE TABLE IF NOT EXISTS "booking_bookinglog" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "state_before" JSONB,
    "state_after" JSONB,
    "content" TEXT,
    "response_data" TEXT,
    "booking_id" INT REFERENCES "booking_booking" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "booking_bookinglog"."id" IS 'ID';
COMMENT ON COLUMN "booking_bookinglog"."created" IS 'Создано';
COMMENT ON COLUMN "booking_bookinglog"."state_before" IS 'Состояние до';
COMMENT ON COLUMN "booking_bookinglog"."state_after" IS 'Состояние после';
COMMENT ON COLUMN "booking_bookinglog"."content" IS 'Контент';
COMMENT ON COLUMN "booking_bookinglog"."response_data" IS 'Данные ответа';
COMMENT ON COLUMN "booking_bookinglog"."booking_id" IS 'Бронирование';
COMMENT ON TABLE "booking_bookinglog" IS 'Лог броования';
-- downgrade --
DROP TABLE IF EXISTS "booking_bookinglog";
