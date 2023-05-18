-- upgrade --
CREATE TABLE IF NOT EXISTS "booking_mortgage_request" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "initial_fee" INTEGER,
    "income_confirmation_method" VARCHAR(15) NOT NULL,
    "files" JSONB
);
COMMENT ON COLUMN "booking_mortgage_request"."id" IS 'ID';
COMMENT ON COLUMN "booking_mortgage_request"."initial_fee" IS 'Первоначальный взнос';
COMMENT ON COLUMN "booking_mortgage_request"."income_confirmation_method" IS 'Способ подтверждения дохода';
COMMENT ON COLUMN "booking_mortgage_request"."files" IS 'Файлы';

ALTER TABLE "booking_booking" ADD "mortgage_request_id" INT UNIQUE;
ALTER TABLE "booking_booking" ADD FOREIGN KEY (mortgage_request_id) REFERENCES "booking_mortgage_request"(id);

-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "mortgage_request_id";
DROP TABLE IF EXISTS "booking_mortgage_request";
