-- upgrade --
ALTER TABLE "users_checks" DROP COLUMN "status";
-- downgrade --
ALTER TABLE "users_checks" ADD "status" VARCHAR(20);
