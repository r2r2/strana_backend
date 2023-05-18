-- upgrade --
ALTER TABLE "agencies_agency" ADD "checking_account" VARCHAR(20);
ALTER TABLE "agencies_agency" ADD "state_registration_number" VARCHAR(15);
ALTER TABLE "agencies_agency" ADD "signatory_patronymic" VARCHAR(50);
ALTER TABLE "agencies_agency" ADD "legal_address" TEXT;
ALTER TABLE "agencies_agency" ADD "signatory_surname" VARCHAR(50);
ALTER TABLE "agencies_agency" ADD "bank_name" VARCHAR(100);
ALTER TABLE "agencies_agency" ADD "signatory_registry_number" VARCHAR(100);
ALTER TABLE "agencies_agency" ADD "signatory_sign_date" TIMESTAMPTZ;
ALTER TABLE "agencies_agency" ADD "signatory_name" VARCHAR(50);
ALTER TABLE "agencies_agency" ADD "bank_identification_code" VARCHAR(9);
ALTER TABLE "agencies_agency" ADD "correspondent_account" VARCHAR(20);
-- downgrade --
ALTER TABLE "agencies_agency" DROP COLUMN "checking_account";
ALTER TABLE "agencies_agency" DROP COLUMN "state_registration_number";
ALTER TABLE "agencies_agency" DROP COLUMN "signatory_patronymic";
ALTER TABLE "agencies_agency" DROP COLUMN "legal_address";
ALTER TABLE "agencies_agency" DROP COLUMN "signatory_surname";
ALTER TABLE "agencies_agency" DROP COLUMN "bank_name";
ALTER TABLE "agencies_agency" DROP COLUMN "signatory_registry_number";
ALTER TABLE "agencies_agency" DROP COLUMN "signatory_sign_date";
ALTER TABLE "agencies_agency" DROP COLUMN "signatory_name";
ALTER TABLE "agencies_agency" DROP COLUMN "bank_identification_code";
ALTER TABLE "agencies_agency" DROP COLUMN "correspondent_account";
