-- upgrade --
ALTER TABLE "properties_property" ADD "section_id" INT;
ALTER TABLE "buildings_building" ADD "flats_1_min_price" DECIMAL(14,2);
ALTER TABLE "buildings_building" ADD "flats_4_min_price" DECIMAL(14,2);
ALTER TABLE "buildings_building" ADD "name_display" VARCHAR(100);
ALTER TABLE "buildings_building" ADD "flats_0_min_price" DECIMAL(14,2);
ALTER TABLE "buildings_building" ADD "flats_2_min_price" DECIMAL(14,2);
ALTER TABLE "buildings_building" ADD "flats_3_min_price" DECIMAL(14,2);
ALTER TABLE "buildings_building" ADD "kind" VARCHAR(32) NOT NULL  DEFAULT 'RESIDENTIAL';
CREATE TABLE IF NOT EXISTS "buildings_section" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "total_floors" INT,
    "number" VARCHAR(50) NOT NULL  DEFAULT '-',
    "building_id" INT REFERENCES "buildings_building" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "buildings_building"."flats_1_min_price" IS 'Мин цена 1-комн';
COMMENT ON COLUMN "buildings_building"."flats_4_min_price" IS 'Мин цена 4-комн';
COMMENT ON COLUMN "buildings_building"."name_display" IS 'Отображаемое имя';
COMMENT ON COLUMN "buildings_building"."flats_0_min_price" IS 'Мин цена студия';
COMMENT ON COLUMN "buildings_building"."flats_2_min_price" IS 'Мин цена 2-комн';
COMMENT ON COLUMN "buildings_building"."flats_3_min_price" IS 'Мин цена 3-комн';
COMMENT ON COLUMN "buildings_building"."kind" IS 'Тип строения';
COMMENT ON COLUMN "buildings_section"."number" IS 'Название';
COMMENT ON TABLE "buildings_section" IS 'Секция';;
ALTER TABLE "properties_property" ADD CONSTRAINT "fk_properti_building_98344e61" FOREIGN KEY ("section_id") REFERENCES "buildings_section" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "properties_property" DROP CONSTRAINT "fk_properti_building_98344e61";
ALTER TABLE "buildings_building" DROP COLUMN "flats_1_min_price";
ALTER TABLE "buildings_building" DROP COLUMN "flats_4_min_price";
ALTER TABLE "buildings_building" DROP COLUMN "name_display";
ALTER TABLE "buildings_building" DROP COLUMN "flats_0_min_price";
ALTER TABLE "buildings_building" DROP COLUMN "flats_2_min_price";
ALTER TABLE "buildings_building" DROP COLUMN "flats_3_min_price";
ALTER TABLE "buildings_building" DROP COLUMN "kind";
ALTER TABLE "properties_property" DROP COLUMN "section_id";
DROP TABLE IF EXISTS "buildings_section";
