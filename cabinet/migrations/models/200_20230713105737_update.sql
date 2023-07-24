-- upgrade --
ALTER TABLE "projects_project" ADD "card_image_night" VARCHAR(255);
ALTER TABLE "projects_project" ADD "address" VARCHAR(250);
ALTER TABLE "projects_project" ADD "metro_id" INT;
ALTER TABLE "projects_project" ADD "card_image" VARCHAR(255);
ALTER TABLE "projects_project" ADD "project_color" VARCHAR(8)   DEFAULT '#FFFFFF';
ALTER TABLE "projects_project" ADD "card_sky_color" VARCHAR(20) NOT NULL  DEFAULT 'light_blue';
ALTER TABLE "projects_project" ADD "min_flat_area" DECIMAL(7,2);
ALTER TABLE "projects_project" ADD "transport_time" INT;
ALTER TABLE "projects_project" ADD "min_flat_price" INT;
ALTER TABLE "projects_project" ADD "max_flat_area" DECIMAL(7,2);
ALTER TABLE "projects_project" ADD "title" VARCHAR(200);
ALTER TABLE "projects_project" ADD "transport_id" INT;
ALTER TABLE "cities_city" ADD "color" VARCHAR(8) NOT NULL  DEFAULT '#FFFFFF';
CREATE TABLE IF NOT EXISTS "cities_metroline" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "color" VARCHAR(8) NOT NULL  DEFAULT '#FF0000',
    "city_id" INT REFERENCES "cities_city" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "cities_metroline"."name" IS 'Название';
COMMENT ON COLUMN "cities_metroline"."color" IS 'Цвет';
COMMENT ON TABLE "cities_metroline" IS 'Модель линии метро';;
CREATE TABLE IF NOT EXISTS "cities_metro" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(32) NOT NULL,
    "latitude" DECIMAL(9,6),
    "longitude" DECIMAL(9,6),
    "order" INT NOT NULL  DEFAULT 0,
    "line_id" INT REFERENCES "cities_metroline" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_cities_metr_order_7565f9" ON "cities_metro" ("order");
COMMENT ON COLUMN "projects_project"."card_image_night" IS 'Изображение на карточке (ночь)';
COMMENT ON COLUMN "projects_project"."card_image" IS 'Изображение на карточке';
COMMENT ON COLUMN "projects_project"."project_color" IS 'Цвет';
COMMENT ON COLUMN "projects_project"."card_sky_color" IS 'Цвет неба на карточке проекта';
COMMENT ON COLUMN "projects_project"."min_flat_area" IS 'Мин площадь квартиры';
COMMENT ON COLUMN "projects_project"."transport_time" IS 'Время в пути';
COMMENT ON COLUMN "projects_project"."min_flat_price" IS 'Мин цена квартиры';
COMMENT ON COLUMN "projects_project"."max_flat_area" IS 'Макс площадь квартиры';
COMMENT ON COLUMN "projects_project"."title" IS 'Заголовок';
COMMENT ON COLUMN "projects_project"."address" IS 'Адрес';
COMMENT ON COLUMN "cities_city"."color" IS 'Цвет';
COMMENT ON COLUMN "cities_metro"."name" IS 'Название';
COMMENT ON COLUMN "cities_metro"."latitude" IS 'Широта';
COMMENT ON COLUMN "cities_metro"."longitude" IS 'Долгота';
COMMENT ON COLUMN "cities_metro"."order" IS 'Порядок';
COMMENT ON TABLE "cities_metro" IS 'Модель метро';;
CREATE TABLE IF NOT EXISTS "cities_transport" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "icon" VARCHAR(255),
    "icon_content" TEXT
);
COMMENT ON COLUMN "cities_transport"."name" IS 'Название';
COMMENT ON COLUMN "cities_transport"."icon" IS 'Иконка';
COMMENT ON COLUMN "cities_transport"."icon_content" IS 'Контент иконки';
COMMENT ON TABLE "cities_transport" IS 'Способ передвижения';;
ALTER TABLE "projects_project" ADD CONSTRAINT "fk_projects_cities_m_18489271" FOREIGN KEY ("metro_id") REFERENCES "cities_metro" ("id") ON DELETE SET NULL;
ALTER TABLE "projects_project" ADD CONSTRAINT "fk_projects_cities_t_aa4cd751" FOREIGN KEY ("transport_id") REFERENCES "cities_transport" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "projects_project" DROP CONSTRAINT "fk_projects_cities_t_aa4cd751";
ALTER TABLE "projects_project" DROP CONSTRAINT "fk_projects_cities_m_18489271";
ALTER TABLE "cities_city" DROP COLUMN "color";
ALTER TABLE "projects_project" DROP COLUMN "card_image_night";
ALTER TABLE "projects_project" DROP COLUMN "address";
ALTER TABLE "projects_project" DROP COLUMN "metro_id";
ALTER TABLE "projects_project" DROP COLUMN "card_image";
ALTER TABLE "projects_project" DROP COLUMN "project_color";
ALTER TABLE "projects_project" DROP COLUMN "card_sky_color";
ALTER TABLE "projects_project" DROP COLUMN "min_flat_area";
ALTER TABLE "projects_project" DROP COLUMN "transport_time";
ALTER TABLE "projects_project" DROP COLUMN "min_flat_price";
ALTER TABLE "projects_project" DROP COLUMN "max_flat_area";
ALTER TABLE "projects_project" DROP COLUMN "title";
ALTER TABLE "projects_project" DROP COLUMN "transport_id";
DROP TABLE IF EXISTS "cities_metro";
DROP TABLE IF EXISTS "cities_metroline";
DROP TABLE IF EXISTS "cities_transport";
