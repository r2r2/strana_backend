-- upgrade --
ALTER TABLE "booking_booking" ALTER COLUMN "created" TYPE TIMESTAMPTZ USING "created"::TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "booking_booking" ALTER COLUMN "created" TYPE TIMESTAMPTZ USING "created"::TIMESTAMPTZ;
