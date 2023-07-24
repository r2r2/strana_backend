-- upgrade --
ALTER TABLE "users_checks" ADD "amocrm_id" INT;
ALTER TABLE "users_checks" ADD "send_admin_email" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "users_checks" DROP COLUMN "amocrm_id";
ALTER TABLE "users_checks" DROP COLUMN "send_admin_email";
