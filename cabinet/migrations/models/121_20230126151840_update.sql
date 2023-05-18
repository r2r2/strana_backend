-- upgrade --
ALTER TABLE "booking_booking" DROP COLUMN "amocrm_status_name";
ALTER TABLE "booking_booking" ALTER COLUMN "amocrm_status_id" TYPE INT USING "amocrm_status_id"::INT;
ALTER TABLE "booking_booking" ADD CONSTRAINT "fk_booking__amocrm_s_e79b52b5" FOREIGN KEY ("amocrm_status_id") REFERENCES "amocrm_statuses" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "booking_booking" DROP CONSTRAINT "fk_booking__amocrm_s_e79b52b5";
ALTER TABLE "booking_booking" ADD "amocrm_status_name" VARCHAR(200);
ALTER TABLE "booking_booking" ALTER COLUMN "amocrm_status_id" TYPE INT USING "amocrm_status_id"::INT;
