-- upgrade --
ALTER TABLE "users_unique_statuses" ADD COLUMN IF NOT EXISTS "stop_check" BOOL NOT NULL  DEFAULT False;

UPDATE "users_unique_statuses"
SET "stop_check" = True
WHERE slug = 'not_unique' or slug = 'can_dispute';
-- downgrade --
ALTER TABLE "users_unique_statuses" DROP COLUMN "stop_check";
