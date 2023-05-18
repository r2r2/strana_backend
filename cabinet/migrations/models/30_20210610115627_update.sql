-- upgrade --
ALTER TABLE "users_checks" ADD "requested" TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "users_checks" DROP COLUMN "requested";
