-- upgrade --
ALTER TABLE "users_interests" ADD "slug" VARCHAR(20) DEFAULT 'manager';
-- downgrade --
ALTER TABLE "users_interests" DROP COLUMN "slug";
