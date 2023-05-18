-- upgrade --
ALTER TABLE "booking_booking" ADD "amocrm_agent_data_validated" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "booking_booking" ADD "ddu_created" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "booking_booking" ADD "amocrm_ddu_uploaded_by_lawyer" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "booking_booking" ADD "ddu_approved" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "booking_booking" ADD "escrow_uploaded" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "booking_booking" ADD "amocrm_signing_date_set" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "booking_booking" ADD "amocrm_signed" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "booking_booking" DROP COLUMN "mortgage_was_approved_by_agent";
ALTER TABLE "booking_ddu" DROP COLUMN "accepted_by_client";
-- downgrade --
ALTER TABLE "booking_booking" ADD "mortgage_was_approved_by_agent" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "booking_ddu" ADD "accepted_by_client" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "booking_booking" DROP COLUMN "amocrm_agent_data_validated";
ALTER TABLE "booking_booking" DROP COLUMN "ddu_created";
ALTER TABLE "booking_booking" DROP COLUMN "amocrm_ddu_uploaded_by_lawyer";
ALTER TABLE "booking_booking" DROP COLUMN "ddu_approved";
ALTER TABLE "booking_booking" DROP COLUMN "escrow_uploaded";
ALTER TABLE "booking_booking" DROP COLUMN "amocrm_signing_date_set";
ALTER TABLE "booking_booking" DROP COLUMN "amocrm_signed";