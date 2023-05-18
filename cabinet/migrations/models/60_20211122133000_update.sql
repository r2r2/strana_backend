-- upgrade --
ALTER TABLE "booking_bank_contact_info" DROP COLUMN "specialist_name";
ALTER TABLE "booking_bank_contact_info" DROP COLUMN "specialist_phone";
ALTER TABLE "booking_bank_contact_info" DROP COLUMN "specialist_email";
-- downgrade --
ALTER TABLE "booking_bank_contact_info" ADD "specialist_name" VARCHAR(100);
ALTER TABLE "booking_bank_contact_info" ADD "specialist_phone" VARCHAR(100);
ALTER TABLE "booking_bank_contact_info" ADD "specialist_email" VARCHAR(100);
