-- upgrade --
ALTER TABLE "main_page_manager" ADD "position" VARCHAR(512);
ALTER TABLE "main_page_manager" ADD "photo" VARCHAR(2000);
-- downgrade --
ALTER TABLE "main_page_manager" DROP COLUMN "position";
ALTER TABLE "main_page_manager" DROP COLUMN "photo";
