-- upgrade --
ALTER TABLE "users_checks_history" ADD "client_phone" VARCHAR(20);
ALTER TABLE "users_checks_history" ALTER COLUMN "created_at" TYPE DATE USING "created_at"::DATE;
-- downgrade --
ALTER TABLE "users_checks_history" DROP COLUMN "client_phone";
ALTER TABLE "users_checks_history" ALTER COLUMN "created_at" TYPE TIMESTAMPTZ USING "created_at"::TIMESTAMPTZ;