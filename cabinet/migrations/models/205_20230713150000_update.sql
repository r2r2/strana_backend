-- upgrade --
ALTER TABLE "users_unique_statuses" RENAME COLUMN "text_color" TO "color";
ALTER TABLE "users_unique_statuses" ADD IF NOT EXISTS "border_color" VARCHAR(7)   DEFAULT '#8F00FF';
-- downgrade --
ALTER TABLE "users_unique_statuses" RENAME COLUMN "color" TO "text_color";
ALTER TABLE "users_unique_statuses" DROP COLUMN "border_color";
