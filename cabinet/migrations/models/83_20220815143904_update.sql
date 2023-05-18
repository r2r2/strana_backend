-- upgrade --
ALTER TABLE "booking_ddu_participant" ADD "inn" VARCHAR(50);
-- downgrade --
ALTER TABLE "booking_ddu_participant" DROP COLUMN "inn";
