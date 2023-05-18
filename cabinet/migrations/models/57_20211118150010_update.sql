-- upgrade --
ALTER TABLE "booking_booking" RENAME COLUMN "amocrm_online_purchase_started" TO "online_purchase_started";
ALTER TABLE "booking_booking" RENAME COLUMN "amocrm_purchase_start_datetime" TO "purchase_start_datetime";
ALTER TABLE "booking_booking" ADD "payment_method_selected" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "booking_booking" ADD "client_has_an_approved_mortgage" BOOL;
ALTER TABLE "booking_booking" ADD "client_needs_help_with_mortgage" BOOL;
ALTER TABLE "booking_booking" DROP COLUMN "mortgage_approved";
ALTER TABLE "booking_ddu" ADD "accepted_by_client" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "booking_ddu" DROP COLUMN "accepted_by_client";
ALTER TABLE "booking_booking" ADD "mortgage_approved" BOOL;
ALTER TABLE "booking_booking" RENAME COLUMN "purchase_start_datetime" TO "amocrm_purchase_start_datetime";
ALTER TABLE "booking_booking" RENAME COLUMN "online_purchase_started" TO "amocrm_online_purchase_started";
ALTER TABLE "booking_booking" DROP COLUMN "payment_method_selected";
ALTER TABLE "booking_booking" DROP COLUMN "client_has_an_approved_mortgage";
ALTER TABLE "booking_booking" DROP COLUMN "client_needs_help_with_mortgage";
