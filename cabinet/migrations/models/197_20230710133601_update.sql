-- upgrade --
ALTER TABLE "users_user_pinning_status" ADD "unique_status_id" INT;
ALTER TABLE "users_user_pinning_status" ADD CONSTRAINT "fk_users_us_users_un_1e590a3a" FOREIGN KEY ("unique_status_id") REFERENCES "users_unique_statuses" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "users_user_pinning_status" DROP CONSTRAINT "fk_users_us_users_un_1e590a3a";
ALTER TABLE "users_user_pinning_status" DROP COLUMN "unique_status_id";
