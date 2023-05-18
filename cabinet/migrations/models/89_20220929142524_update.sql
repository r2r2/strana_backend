-- upgrade --
ALTER TABLE "booking_booking" ADD "amocrm_status_id" INT;
ALTER TABLE "booking_booking" ADD "amocrm_status_name" VARCHAR(200);
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "amocrm_status_id";
ALTER TABLE "booking_booking" DROP COLUMN "amocrm_status_name";
