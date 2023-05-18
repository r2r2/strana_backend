-- upgrade --
ALTER TABLE "users_user" ADD "passport_series" VARCHAR(20);
ALTER TABLE "users_user" ADD "passport_number" VARCHAR(20);
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "passport_series";
ALTER TABLE "users_user" DROP COLUMN "passport_number";
