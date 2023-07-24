-- upgrade --
ALTER TABLE "cities_city" ADD "global_id" VARCHAR(50);
ALTER TABLE "dashboard_element" ADD "slug" VARCHAR(15);
ALTER TABLE "menus_menu" RENAME COLUMN "hide_mobile" TO "hide_desktop";
-- downgrade --
ALTER TABLE "cities_city" DROP COLUMN "global_id";
ALTER TABLE "menus_menu" RENAME COLUMN "hide_desktop" TO "hide_mobile";
ALTER TABLE "dashboard_element" DROP COLUMN "slug";
