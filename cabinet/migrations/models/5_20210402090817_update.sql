-- upgrade --
ALTER TABLE "booking_booking" ADD "payment_order_number" UUID NOT NULL;
ALTER TABLE "booking_booking" RENAME COLUMN "stage" TO "amocrm_stage";
ALTER TABLE "booking_booking" ADD "payment_currency" INT NOT NULL  DEFAULT 643;
ALTER TABLE "booking_booking" RENAME COLUMN "substage" TO "amocrm_substage";
ALTER TABLE "booking_booking" ADD "payment_amount" DECIMAL(15,2);
ALTER TABLE "booking_booking" ADD "payment_id" UUID;
ALTER TABLE "booking_booking" ADD "payment_page_view" VARCHAR(50) NOT NULL  DEFAULT 'DESKTOP';
ALTER TABLE "booking_booking" ADD "payment_status" INT;
ALTER TABLE "booking_booking" DROP COLUMN "amount";
ALTER TABLE "booking_booking" DROP COLUMN "bank_id";
ALTER TABLE "booking_booking" DROP COLUMN "currency";
ALTER TABLE "booking_booking" DROP COLUMN "order_number";
-- downgrade --
ALTER TABLE "booking_booking" ADD "amount" DECIMAL(15,2);
ALTER TABLE "booking_booking" RENAME COLUMN "amocrm_substage" TO "substage";
ALTER TABLE "booking_booking" RENAME COLUMN "amocrm_stage" TO "stage";
ALTER TABLE "booking_booking" ADD "bank_id" UUID;
ALTER TABLE "booking_booking" ADD "currency" INT NOT NULL  DEFAULT 643;
ALTER TABLE "booking_booking" ADD "order_number" UUID NOT NULL;
ALTER TABLE "booking_booking" DROP COLUMN "payment_order_number";
ALTER TABLE "booking_booking" DROP COLUMN "payment_currency";
ALTER TABLE "booking_booking" DROP COLUMN "payment_amount";
ALTER TABLE "booking_booking" DROP COLUMN "payment_id";
ALTER TABLE "booking_booking" DROP COLUMN "payment_page_view";
ALTER TABLE "booking_booking" DROP COLUMN "payment_status";
