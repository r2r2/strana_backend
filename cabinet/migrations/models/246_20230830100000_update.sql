-- upgrade --
ALTER TABLE "properties_property" ALTER COLUMN "plan_png" TYPE VARCHAR(500) USING "plan_png"::VARCHAR(500);
ALTER TABLE "properties_property" ALTER COLUMN "plan" TYPE VARCHAR(500) USING "plan"::VARCHAR(500);
-- downgrade --
ALTER TABLE "properties_property" ALTER COLUMN "plan_png" TYPE VARCHAR(300) USING "plan_png"::VARCHAR(300);
ALTER TABLE "properties_property" ALTER COLUMN "plan" TYPE VARCHAR(300) USING "plan"::VARCHAR(300);
