-- upgrade --
ALTER TABLE "users_user" ADD "is_contracted" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "is_contracted";
