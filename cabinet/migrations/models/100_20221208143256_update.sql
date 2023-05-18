-- upgrade --
ALTER TABLE "users_checks" ALTER COLUMN "admin_comment" TYPE TEXT USING "admin_comment"::TEXT;
ALTER TABLE "users_checks" ALTER COLUMN "comment" TYPE TEXT USING "comment"::TEXT;
-- downgrade --
ALTER TABLE "users_checks" ALTER COLUMN "admin_comment" TYPE VARCHAR(2000) USING "admin_comment"::VARCHAR(2000);
ALTER TABLE "users_checks" ALTER COLUMN "comment" TYPE VARCHAR(2000) USING "comment"::VARCHAR(2000);
