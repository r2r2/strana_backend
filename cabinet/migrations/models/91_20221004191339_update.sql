-- upgrade --
ALTER TABLE "users_interests" ADD "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE "users_interests" ADD "id" SERIAL NOT NULL PRIMARY KEY;
ALTER TABLE "users_interests" ADD "created_by_id" INT REFERENCES "users_user" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "users_interests" DROP COLUMN "created_at";
ALTER TABLE "users_interests" DROP COLUMN "created_by_id";
ALTER TABLE "users_interests" DROP COLUMN "id";
