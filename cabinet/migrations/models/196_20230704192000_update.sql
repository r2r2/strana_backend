-- upgrade --
ALTER TABLE "users_checks_history" ADD "unique_status_id" INT;
ALTER TABLE "users_checks_history" ADD CONSTRAINT "fk_users_ch_users_unique_status" FOREIGN KEY ("unique_status_id") REFERENCES "users_unique_statuses" ("id") ON DELETE CASCADE;
ALTER TABLE "users_checks" ADD "unique_status_id" INT;
ALTER TABLE "users_checks" ADD CONSTRAINT "fk_users_checks_users_unique_status" FOREIGN KEY ("unique_status_id") REFERENCES "users_unique_statuses" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "users_checks_history" DROP CONSTRAINT "fk_users_ch_users_unique_status";
ALTER TABLE "users_checks_history" DROP COLUMN "unique_status_id";
ALTER TABLE "users_checks" DROP CONSTRAINT "fk_users_checks_users_unique_status";
ALTER TABLE "users_checks" DROP COLUMN "unique_status_id";
