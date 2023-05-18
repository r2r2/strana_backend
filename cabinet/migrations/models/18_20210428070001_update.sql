-- upgrade --
ALTER TABLE "users_user" ADD "is_imported" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "users_user" ADD "email_token" VARCHAR(100);
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "is_imported";
ALTER TABLE "users_user" DROP COLUMN "email_token";
