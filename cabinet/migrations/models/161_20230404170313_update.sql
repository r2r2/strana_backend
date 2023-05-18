-- upgrade --
ALTER TABLE "users_user" ADD "assignation_comment" TEXT;
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "assignation_comment";
