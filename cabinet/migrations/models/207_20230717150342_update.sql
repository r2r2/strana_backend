-- upgrade --
ALTER TABLE "projects_project" ALTER COLUMN "card_image_night" TYPE VARCHAR(255) USING "card_image_night"::VARCHAR(255);
ALTER TABLE "projects_project" ALTER COLUMN "card_image" TYPE VARCHAR(255) USING "card_image"::VARCHAR(255);
ALTER TABLE "buildings_building" ADD "show_in_paid_booking" BOOL NOT NULL  DEFAULT True;
ALTER TABLE "buildings_section" ADD "name" VARCHAR(50);
ALTER TABLE "floors_floor" ADD "section_id" INT;
ALTER TABLE "floors_floor" ADD CONSTRAINT "fk_floors_f_building_46338048" FOREIGN KEY ("section_id") REFERENCES "buildings_section" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "floors_floor" DROP CONSTRAINT "fk_floors_f_building_46338048";
ALTER TABLE "floors_floor" DROP COLUMN "section_id";
ALTER TABLE "projects_project" ALTER COLUMN "card_image_night" TYPE VARCHAR(255) USING "card_image_night"::VARCHAR(255);
ALTER TABLE "projects_project" ALTER COLUMN "card_image" TYPE VARCHAR(255) USING "card_image"::VARCHAR(255);
ALTER TABLE "buildings_building" DROP COLUMN "show_in_paid_booking";
ALTER TABLE "buildings_section" DROP COLUMN "name";
