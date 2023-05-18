-- upgrade --
ALTER TABLE "users_checks" ADD "comment" VARCHAR(2000);
-- downgrade --
ALTER TABLE "users_checks" DROP COLUMN "comment";
