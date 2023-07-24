-- upgrade --
ALTER TABLE "users_unique_statuses" ADD "can_dispute" BOOLEAN DEFAULT False;
ALTER TABLE "users_checks_terms" ADD "assigned_to_agent" BOOLEAN DEFAULT False;
ALTER TABLE "users_checks_terms" ADD "assigned_to_another_agent" BOOLEAN DEFAULT False;
ALTER TABLE "users_checks_terms" ADD "send_admin_email" BOOLEAN DEFAULT False;
ALTER TABLE "users_checks_terms" ADD "unique_status_id" INT;
ALTER TABLE "users_checks_terms" ADD CONSTRAINT "users_checks_terms_unique_status_fkey" FOREIGN KEY ("unique_status_id") REFERENCES "users_unique_statuses" ("id") ON DELETE CASCADE;
ALTER TABLE "users_pinning_status" ADD "assigned_to_agent" BOOLEAN DEFAULT False;
ALTER TABLE "users_pinning_status" ADD "assigned_to_another_agent" BOOLEAN DEFAULT False;
ALTER TABLE "users_pinning_status" ADD "unique_status_id" INT;
ALTER TABLE "users_pinning_status" ADD CONSTRAINT "users_pinning_status_unique_status_fkey" FOREIGN KEY ("unique_status_id") REFERENCES "users_unique_statuses" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "users_unique_statuses" DROP COLUMN IF EXISTS "can_dispute";
ALTER TABLE "users_checks_terms" DROP CONSTRAINT IF EXISTS "users_checks_terms_unique_status_fkey";
ALTER TABLE "users_checks_terms" DROP COLUMN IF EXISTS "assigned_to_agent";
ALTER TABLE "users_checks_terms" DROP COLUMN IF EXISTS "assigned_to_another_agent";
ALTER TABLE "users_checks_terms" DROP COLUMN IF EXISTS "send_admin_email";
ALTER TABLE "users_checks_terms" DROP COLUMN IF EXISTS "unique_status_id";
ALTER TABLE "users_pinning_status" DROP CONSTRAINT IF EXISTS "users_pinning_status_unique_status_fkey";
ALTER TABLE "users_pinning_status" DROP COLUMN IF EXISTS "assigned_to_agent";
ALTER TABLE "users_pinning_status" DROP COLUMN IF EXISTS "assigned_to_another_agent";
ALTER TABLE "users_pinning_status" DROP COLUMN IF EXISTS "unique_status_id";
