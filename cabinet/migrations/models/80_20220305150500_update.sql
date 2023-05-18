-- upgrade --
ALTER TABLE "booking_ddu_participant"
    ADD COLUMN is_main_contact BOOLEAN DEFAULT FALSE;
-- downgrade --
ALTER TABLE "booking_ddu_participant"
    DROP COLUMN is_main_contact;