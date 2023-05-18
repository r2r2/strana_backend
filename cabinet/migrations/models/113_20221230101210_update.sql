-- upgrade --
ALTER TABLE "agencies_act" ALTER COLUMN "booking_id" TYPE INT USING "booking_id"::INT;
-- downgrade --
ALTER TABLE "agencies_act" ALTER COLUMN "booking_id" TYPE INT USING "booking_id"::INT;
