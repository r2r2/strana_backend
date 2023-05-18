-- upgrade --
ALTER TABLE "users_checks" ADD "dispute_requested" TIMESTAMPTZ;
ALTER TABLE "users_checks" ADD "status_fixed" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "users_checks" DROP COLUMN "dispute_requested";
ALTER TABLE "users_checks" DROP COLUMN "status_fixed";
