-- upgrade --
ALTER TABLE "booking_booking" ADD "payment_method_id" INT;
ALTER TABLE "booking_booking" ADD "price_id" INT;
ALTER TABLE "booking_booking" ADD CONSTRAINT "fk_booking__payments_5bde4b26" FOREIGN KEY ("price_id") REFERENCES "payments_property_price" ("id") ON DELETE SET NULL;
ALTER TABLE "booking_booking" ADD CONSTRAINT "fk_booking__payments_34d924c9" FOREIGN KEY ("payment_method_id") REFERENCES "payments_payment_method" ("id") ON DELETE SET NULL;
ALTER TABLE "payments_property_price_type" ADD CONSTRAINT "fk_booking__payments_35c813b8" UNIQUE ("slug");
-- downgrade --
ALTER TABLE "booking_booking" DROP CONSTRAINT "fk_booking__payments_5bde4b26";
ALTER TABLE "booking_booking" DROP CONSTRAINT "fk_booking__payments_34d924c9";
ALTER TABLE "booking_booking" DROP CONSTRAINT "fk_booking__payments_35c813b8";
ALTER TABLE "booking_booking" DROP COLUMN "payment_method_id";
ALTER TABLE "booking_booking" DROP COLUMN "price_id";
