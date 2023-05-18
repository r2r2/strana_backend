-- upgrade --
ALTER TABLE "users_checks" ADD "admin_id" INT;
ALTER TABLE "users_checks" ADD "dispute_agent_id" INT;
ALTER TABLE "users_checks" ADD CONSTRAINT "fk_users_ch_users_us_a63099e3" FOREIGN KEY ("dispute_agent_id") REFERENCES "users_user" ("id") ON DELETE SET NULL;
ALTER TABLE "users_checks" ADD CONSTRAINT "fk_users_ch_users_us_fda784b8" FOREIGN KEY ("admin_id") REFERENCES "users_user" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "users_checks" DROP CONSTRAINT "fk_users_ch_users_us_fda784b8";
ALTER TABLE "users_checks" DROP CONSTRAINT "fk_users_ch_users_us_a63099e3";
ALTER TABLE "users_checks" DROP COLUMN "admin_id";
ALTER TABLE "users_checks" DROP COLUMN "dispute_agent_id";
