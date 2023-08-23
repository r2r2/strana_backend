-- upgrade --
ALTER TABLE "menus_menu" ALTER COLUMN "name" TYPE VARCHAR(50) USING "name"::VARCHAR(50);
ALTER TABLE "menus_menu" ALTER COLUMN "link" TYPE VARCHAR(100) USING "link"::VARCHAR(100);
ALTER TABLE "dashboard_element" DROP COLUMN "slug";
-- downgrade --
ALTER TABLE "menus_menu" ALTER COLUMN "name" TYPE VARCHAR(15) USING "name"::VARCHAR(15);
ALTER TABLE "menus_menu" ALTER COLUMN "link" TYPE VARCHAR(50) USING "link"::VARCHAR(50);
ALTER TABLE "dashboard_element" ADD "slug" VARCHAR(15);
