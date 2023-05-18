-- upgrade --
ALTER TABLE "users_checks" ADD "admin_comment" VARCHAR(2000);
ALTER TABLE "users_checks" ALTER COLUMN "comment" TYPE VARCHAR(2000) USING "comment"::VARCHAR(2000);
-- downgrade --
ALTER TABLE "users_checks" DROP COLUMN "admin_comment";
ALTER TABLE "users_checks" ALTER COLUMN "comment" TYPE VARCHAR(2000) USING "comment"::VARCHAR(2000);
