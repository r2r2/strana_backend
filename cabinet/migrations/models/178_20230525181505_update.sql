-- upgrade --
ALTER TABLE "notifications_assignclient" ADD IF NOT EXISTS "success_assign_text" TEXT;
ALTER TABLE "notifications_assignclient" ADD IF NOT EXISTS "success_unassign_text" TEXT;
ALTER TABLE "notifications_assignclient" ADD IF NOT EXISTS "title" VARCHAR(255);
-- downgrade --
ALTER TABLE "notifications_assignclient" DROP COLUMN IF EXISTS "success_assign_text";
ALTER TABLE "notifications_assignclient" DROP COLUMN IF EXISTS "success_unassign_text";
ALTER TABLE "notifications_assignclient" DROP COLUMN IF EXISTS "title";
