-- upgrade --
ALTER TABLE "users_checks" DROP COLUMN "state";
-- downgrade --
ALTER TABLE "users_checks" ADD "state" VARCHAR(20);
