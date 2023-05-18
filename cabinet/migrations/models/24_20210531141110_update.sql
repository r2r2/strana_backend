-- upgrade --
ALTER TABLE "users_user" ADD "is_onboarded" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "properties_property" ADD "premise" VARCHAR(30)   DEFAULT 'RESIDENTIAL';
ALTER TABLE "properties_property" ALTER COLUMN "plan_png" TYPE VARCHAR(300) USING "plan_png"::VARCHAR(300);
ALTER TABLE "properties_property" ALTER COLUMN "plan" TYPE VARCHAR(300) USING "plan"::VARCHAR(300);
ALTER TABLE "tips_tip" ALTER COLUMN "image" TYPE VARCHAR(500) USING "image"::VARCHAR(500);
-- downgrade --
ALTER TABLE "tips_tip" ALTER COLUMN "image" TYPE VARCHAR(500) USING "image"::VARCHAR(500);
ALTER TABLE "users_user" DROP COLUMN "is_onboarded";
ALTER TABLE "properties_property" DROP COLUMN "premise";
ALTER TABLE "properties_property" ALTER COLUMN "plan_png" TYPE VARCHAR(300) USING "plan_png"::VARCHAR(300);
ALTER TABLE "properties_property" ALTER COLUMN "plan" TYPE VARCHAR(300) USING "plan"::VARCHAR(300);
