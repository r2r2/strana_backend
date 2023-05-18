-- upgrade --
ALTER TABLE "users_user" ADD "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE "agencies_agency" ADD "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "created_at";
ALTER TABLE "agencies_agency" DROP COLUMN "created_at";
