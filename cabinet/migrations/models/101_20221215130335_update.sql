-- upgrade --
ALTER TABLE "booking_booking" ALTER COLUMN "commission_value" TYPE DECIMAL(15,2) USING "commission_value"::DECIMAL(15,2);
ALTER TABLE "booking_booking" ALTER COLUMN "commission" TYPE DECIMAL(15,2) USING "commission"::DECIMAL(15,2);
ALTER TABLE "booking_booking" ALTER COLUMN "decremented" TYPE BOOL USING "decremented"::BOOL;
ALTER TABLE "booking_booking" ALTER COLUMN "start_commission" TYPE DECIMAL(15,2) USING "start_commission"::DECIMAL(15,2);
-- downgrade --
ALTER TABLE "booking_booking" ALTER COLUMN "commission_value" TYPE BIGINT USING "commission_value"::BIGINT;
ALTER TABLE "booking_booking" ALTER COLUMN "commission" TYPE DECIMAL(15,2) USING "commission"::DECIMAL(15,2);
ALTER TABLE "booking_booking" ALTER COLUMN "decremented" TYPE BOOL USING "decremented"::BOOL;
ALTER TABLE "booking_booking" ALTER COLUMN "start_commission" TYPE DECIMAL(15,2) USING "start_commission"::DECIMAL(15,2);
