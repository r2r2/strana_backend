-- upgrade --
ALTER TABLE "users_user" ADD "type" VARCHAR(20) NOT NULL  DEFAULT 'client';
-- downgrade --
ALTER TABLE "users_user" DROP COLUMN "type";
