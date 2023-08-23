-- upgrade --
ALTER TABLE "users_checks_terms" ADD COLUMN IF NOT EXISTS "comment" TEXT;
ALTER TABLE "users_checks_terms" DROP COLUMN IF EXISTS "unique_value";
ALTER TABLE "users_checks_terms" ALTER COLUMN "assigned_to_agent" DROP DEFAULT;
ALTER TABLE "users_checks_terms" ALTER COLUMN "assigned_to_another_agent" DROP DEFAULT;
ALTER TABLE "users_pinning_status" DROP COLUMN IF EXISTS "result";
ALTER TABLE "users_pinning_status" ADD COLUMN IF NOT EXISTS "comment" TEXT;
ALTER TABLE "users_pinning_status" DROP COLUMN IF EXISTS "assigned_to_agent";
ALTER TABLE "users_pinning_status" DROP COLUMN IF EXISTS "assigned_to_another_agent";

-- downgrade --
ALTER TABLE "users_checks_terms" DROP COLUMN "comment";
ALTER TABLE "users_checks_terms" ADD COLUMN "unique_value" varchar(28);
ALTER TABLE "users_checks_terms" ALTER COLUMN "assigned_to_agent" SET DEFAULT false;
ALTER TABLE "users_checks_terms" ALTER COLUMN "assigned_to_another_agent" SET DEFAULT false;
ALTER TABLE "users_pinning_status" ADD COLUMN "result" varchar(36);
ALTER TABLE "users_pinning_status" DROP COLUMN "comment";
ALTER TABLE "users_pinning_status" ADD COLUMN "assigned_to_agent" boolean;
ALTER TABLE "users_pinning_status" ADD COLUMN "assigned_to_another_agent" boolean;

