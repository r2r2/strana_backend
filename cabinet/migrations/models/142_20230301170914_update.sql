-- upgrade --
ALTER TABLE "users_checks_history" ALTER COLUMN "created_at" TYPE TIMESTAMPTZ USING "created_at"::TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "users_checks_history" ALTER COLUMN "created_at" TYPE DATE USING "created_at"::DATE;