-- upgrade --
ALTER TABLE "users_user" ADD "origin" VARCHAR(30);
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "origin";
