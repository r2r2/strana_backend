-- upgrade --
ALTER TABLE "users_checks" ADD COLUMN IF NOT EXISTS "term_uid" VARCHAR(255);
ALTER TABLE "users_checks" ADD COLUMN IF NOT EXISTS "term_comment" TEXT;

ALTER TABLE "users_checks_history" ADD COLUMN IF NOT EXISTS "term_uid" VARCHAR(255);
ALTER TABLE "users_checks_history" ADD COLUMN IF NOT EXISTS "term_comment" TEXT;
ALTER TABLE "users_checks_history" ADD COLUMN IF NOT EXISTS "lead_link" TEXT;
ALTER TABLE "users_checks_history" DROP COLUMN IF EXISTS "status";

-- downgrade --
ALTER TABLE "users_checks" DROP COLUMN IF EXISTS "term_uid";
ALTER TABLE "users_checks" DROP COLUMN IF EXISTS "term_comment";

ALTER TABLE "users_checks_history" DROP COLUMN IF EXISTS "term_uid";
ALTER TABLE "users_checks_history" DROP COLUMN IF EXISTS "term_comment";
ALTER TABLE "users_checks_history" DROP COLUMN IF EXISTS "lead_link";
ALTER TABLE "users_checks_history" ADD COLUMN IF NOT EXISTS "status" VARCHAR(255);
