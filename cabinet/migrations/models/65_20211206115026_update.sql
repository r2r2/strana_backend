-- upgrade --
ALTER TABLE "booking_booking" ADD "ddu_upload_url_secret" VARCHAR(100);
ALTER TABLE "booking_booking" DROP COLUMN "ddu_upload_url_id";
DROP TABLE IF EXISTS "ddu_upload_url_ddu_upload_url";
-- downgrade --
ALTER TABLE "booking_booking" ADD "ddu_upload_url_id" INT  UNIQUE;
ALTER TABLE "booking_booking" DROP COLUMN "ddu_upload_url_secret";
CREATE TABLE IF NOT EXISTS "ddu_upload_url_ddu_upload_url" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "secret" VARCHAR(100)
);
