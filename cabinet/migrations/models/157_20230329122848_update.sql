-- upgrade --
ALTER TABLE "users_user" ADD "interested_sub" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "interested_sub";
