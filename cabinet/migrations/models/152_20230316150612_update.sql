-- upgrade --
ALTER TABLE "users_user" ADD "receive_admin_emails" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "receive_admin_emails";
