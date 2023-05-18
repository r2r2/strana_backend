-- upgrade --
ALTER TABLE "booking_ddu_participant" ADD "marital_status" VARCHAR(24);
ALTER TABLE "booking_ddu_participant" ADD "is_older_than_fourteen" BOOL;
ALTER TABLE "booking_ddu_participant" ALTER COLUMN "passport_issued_by" DROP NOT NULL;
ALTER TABLE "booking_ddu_participant" ALTER COLUMN "passport_issued_date" DROP NOT NULL;
ALTER TABLE "booking_ddu_participant" ALTER COLUMN "passport_department_code" DROP NOT NULL;
ALTER TABLE "booking_ddu_participant" ALTER COLUMN "passport_serial" DROP NOT NULL;
ALTER TABLE "booking_ddu_participant" ALTER COLUMN "passport_number" DROP NOT NULL;
-- downgrade --
ALTER TABLE "booking_ddu_participant" DROP COLUMN "marital_status";
ALTER TABLE "booking_ddu_participant" DROP COLUMN "is_older_than_fourteen";
ALTER TABLE "booking_ddu_participant" ALTER COLUMN "passport_issued_by" SET NOT NULL;
ALTER TABLE "booking_ddu_participant" ALTER COLUMN "passport_issued_date" SET NOT NULL;
ALTER TABLE "booking_ddu_participant" ALTER COLUMN "passport_department_code" SET NOT NULL;
ALTER TABLE "booking_ddu_participant" ALTER COLUMN "passport_serial" SET NOT NULL;
ALTER TABLE "booking_ddu_participant" ALTER COLUMN "passport_number" SET NOT NULL;
