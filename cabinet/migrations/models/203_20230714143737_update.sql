-- upgrade --
ALTER TABLE "projects_project" ADD "show_in_paid_booking" BOOL NOT NULL  DEFAULT True;
ALTER TABLE "cities_city" ADD "short_name" VARCHAR(50);
-- downgrade --
ALTER TABLE "cities_city" DROP COLUMN "short_name";
ALTER TABLE "projects_project" DROP COLUMN "show_in_paid_booking";
