-- upgrade --
ALTER TABLE "users_user" ADD "change_email" VARCHAR(100);
ALTER TABLE "users_user" ADD "change_email_token" VARCHAR(100);
ALTER TABLE "users_user" ADD "change_phone" VARCHAR(20);
ALTER TABLE "users_user" ADD "phone_token" VARCHAR(100);
ALTER TABLE "users_user" ADD "change_phone_token" VARCHAR(100);
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "change_email";
ALTER TABLE "users_user" DROP COLUMN "change_email_token";
ALTER TABLE "users_user" DROP COLUMN "change_phone";
ALTER TABLE "users_user" DROP COLUMN "phone_token";
ALTER TABLE "users_user" DROP COLUMN "change_phone_token";
