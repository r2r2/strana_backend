-- upgrade --
CREATE UNIQUE INDEX "uid_booking_boo_amocrm__b91680" ON "booking_booking" ("amocrm_id");
-- downgrade --
DROP INDEX "idx_booking_boo_amocrm__b91680";
