-- upgrade --
ALTER TABLE "booking_booking" ADD "online_purchase_id" VARCHAR(9);
COMMENT ON COLUMN "booking_booking"."online_purchase_id" IS 'ID онлайн-покупки';
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "online_purchase_id";
