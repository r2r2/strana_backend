-- upgrade --
ALTER TABLE "booking_booking" ADD "files" JSONB;
ALTER TABLE "booking_booking" ADD "ddu_upload_url_id" INT  UNIQUE;
CREATE TABLE IF NOT EXISTS "ddu_upload_url_ddu_upload_url" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "secret" VARCHAR(100)
);
COMMENT ON COLUMN "booking_booking"."files" IS 'Файлы';
COMMENT ON COLUMN "booking_booking"."ddu_upload_url_id" IS 'Url загрузки ДДУ';
COMMENT ON COLUMN "ddu_upload_url_ddu_upload_url"."id" IS 'ID';
COMMENT ON COLUMN "ddu_upload_url_ddu_upload_url"."secret" IS 'Секретная часть URL-а';
COMMENT ON TABLE "ddu_upload_url_ddu_upload_url" IS 'URL-ы загрузки ДДУ юристом.';;
ALTER TABLE "booking_mortgage_request" DROP COLUMN "initial_fee";
ALTER TABLE "booking_mortgage_request" DROP COLUMN "income_confirmation_method";
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "files";
ALTER TABLE "booking_booking" DROP COLUMN "ddu_upload_url_id";
ALTER TABLE "booking_mortgage_request" ADD "initial_fee" INT;
ALTER TABLE "booking_mortgage_request" ADD "income_confirmation_method" VARCHAR(15) NOT NULL;
DROP TABLE IF EXISTS "ddu_upload_url_ddu_upload_url";
