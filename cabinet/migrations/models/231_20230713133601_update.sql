-- upgrade --
ALTER TABLE "booking_booking" ADD "final_discount" DECIMAL(15,2);
ALTER TABLE "booking_booking" ADD "final_additional_options" DECIMAL(15,2);
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "final_discount";
ALTER TABLE "booking_booking" DROP COLUMN "final_additional_options";
