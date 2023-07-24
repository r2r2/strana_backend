-- upgrade --
ALTER TABLE "users_user" ADD IF NOT EXISTS "auth_last_at" TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "auth_last_at";
