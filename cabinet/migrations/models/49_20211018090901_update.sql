-- upgrade --
ALTER TABLE "booking_booking" ADD "amocrm_online_purchase_started" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "booking_booking" ADD "amocrm_purchase_start_datetime" TIMESTAMPTZ;
ALTER TABLE "booking_booking" ADD "amocrm_purchase_status" VARCHAR(100);
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "amocrm_online_purchase_started";
ALTER TABLE "booking_booking" DROP COLUMN "amocrm_purchase_start_datetime";
ALTER TABLE "booking_booking" DROP COLUMN "amocrm_purchase_status";
