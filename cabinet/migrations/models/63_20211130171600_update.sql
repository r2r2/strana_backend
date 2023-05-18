-- upgrade --
ALTER TABLE "booking_ddu_participant" ALTER COLUMN "relation_status" DROP NOT NULL;
-- downgrade --
ALTER TABLE "booking_ddu_participant" ALTER COLUMN "relation_status" SET NOT NULL;
