-- upgrade --
ALTER TABLE "users_user" ADD "is_brokers_client" BOOLEAN NOT NULL  DEFAULT FALSE;
ALTER TABLE "users_user" ADD "is_independent_client" BOOLEAN NOT NULL  DEFAULT FALSE;
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "is_brokers_client";
ALTER TABLE "users_user" DROP COLUMN "is_independent_client";
