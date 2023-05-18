-- upgrade --
ALTER TABLE "users_user" ADD "is_test_user" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "is_test_user";