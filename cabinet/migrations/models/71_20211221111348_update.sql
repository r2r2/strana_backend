-- upgrade --
CREATE UNIQUE INDEX "uid_booking_boo_online__200c67" ON "booking_booking" ("online_purchase_id");
-- downgrade --
DROP INDEX "idx_booking_boo_online__200c67";
