-- upgrade --
CREATE TABLE IF NOT EXISTS "booking_webhook_request" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "category" VARCHAR(20) NOT NULL,
    "body" TEXT NOT NULL
);
COMMENT ON COLUMN "booking_webhook_request"."id" IS 'ID';
COMMENT ON COLUMN "booking_webhook_request"."category" IS 'Тип вебхука';
COMMENT ON COLUMN "booking_webhook_request"."body" IS 'Тело запроса';
COMMENT ON TABLE "booking_webhook_request" IS 'Webhook запрос.';
-- downgrade --
DROP TABLE IF EXISTS "booking_webhook_request";
