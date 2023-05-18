-- upgrade --
ALTER TABLE "users_user" ADD "tags" JSONB;
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "tags";
