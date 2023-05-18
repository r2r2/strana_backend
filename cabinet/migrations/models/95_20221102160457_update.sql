-- upgrade --
ALTER TABLE "booking_booking" ADD "final_payment_amount" DECIMAL(15,2);
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "final_payment_amount";
