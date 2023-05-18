-- upgrade --
ALTER TABLE "users_checks_terms" ADD "is_assign_agency_status" VARCHAR(10) NOT NULL DEFAULT 'skip';
ALTER TABLE "users_checks_terms" ALTER COLUMN "is_agent" TYPE VARCHAR(10) USING "is_agent"::VARCHAR(10);
-- downgrade --
ALTER TABLE "users_checks_terms" DROP COLUMN "is_assign_agency_status";
ALTER TABLE "users_checks_terms" ALTER COLUMN "is_agent" TYPE VARCHAR(15) USING "is_agent"::VARCHAR(15);
