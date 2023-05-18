-- upgrade --
ALTER TABLE booking_booking DROP COLUMN mortgage_was_approved_by_agent;
ALTER TABLE booking_booking ADD mortgage_was_approved_by_agent BOOLEAN DEFAULT FALSE NOT NULL;
ALTER TABLE booking_booking ADD ddu_id INTEGER;
ALTER TABLE booking_booking ADD CONSTRAINT booking_booking_ddu_id_fkey FOREIGN KEY (ddu_id) REFERENCES booking_ddu ON DELETE CASCADE;
ALTER TABLE "booking_booking" ADD CONSTRAINT booking_booking_ddu_id_key UNIQUE (ddu_id);
ALTER TABLE booking_booking ADD CONSTRAINT booking_booking_bank_contact_info_id_fkey FOREIGN KEY (bank_contact_info_id) REFERENCES booking_bank_contact_info ON DELETE CASCADE;

-- downgrade --
ALTER TABLE booking_booking DROP COLUMN mortgage_was_approved_by_agent;
ALTER TABLE booking_booking ADD mortgage_was_approved_by_agent BOOLEAN;

ALTER TABLE booking_booking DROP CONSTRAINT booking_booking_ddu_id_fkey;
ALTER TABLE booking_booking DROP CONSTRAINT booking_booking_ddu_id_key;
ALTER TABLE booking_booking DROP CONSTRAINT booking_booking_bank_contact_info_id_fkey;
ALTER TABLE booking_booking DROP COLUMN ddu_id;
