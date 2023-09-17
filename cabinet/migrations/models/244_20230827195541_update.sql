-- upgrade --
CREATE TABLE IF NOT EXISTS "properties_feature" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "backend_id" INT NOT NULL,
    "name" VARCHAR(64) NOT NULL,
    "filter_show" BOOL NOT NULL  DEFAULT True,
    "main_filter_show" BOOL NOT NULL  DEFAULT False,
    "lot_page_show" BOOL NOT NULL  DEFAULT True,
    "icon_show" BOOL NOT NULL  DEFAULT False,
    "icon" VARCHAR(255),
    "icon_flats_show" BOOL NOT NULL  DEFAULT False,
    "icon_hypo" VARCHAR(255),
    "icon_flats" VARCHAR(255),
    "description" TEXT NOT NULL,
    "order" INT NOT NULL  DEFAULT 0,
    "is_button" BOOL NOT NULL  DEFAULT False
);
COMMENT ON COLUMN "properties_feature"."name" IS 'Название';
COMMENT ON COLUMN "properties_feature"."filter_show" IS 'Отображать в фильтре листинга';
COMMENT ON COLUMN "properties_feature"."main_filter_show" IS 'Отображать в фильтре на главной';
COMMENT ON COLUMN "properties_feature"."lot_page_show" IS 'Отображать на странице лота';
COMMENT ON COLUMN "properties_feature"."icon_show" IS 'Отображать иконку';
COMMENT ON COLUMN "properties_feature"."icon" IS 'Иконка';
COMMENT ON COLUMN "properties_feature"."icon_flats_show" IS 'Отображать на странице flats';
COMMENT ON COLUMN "properties_feature"."icon_hypo" IS 'Картинка для тултипа в фильтре';
COMMENT ON COLUMN "properties_feature"."icon_flats" IS 'Иконка для страницы flats';
COMMENT ON COLUMN "properties_feature"."description" IS 'Описание';
COMMENT ON COLUMN "properties_feature"."order" IS 'Очередность';
COMMENT ON COLUMN "properties_feature"."is_button" IS 'Выводить кнопкой';
COMMENT ON TABLE "properties_feature" IS 'Особенность';;
CREATE TABLE "properties_feature_property_through" ("property_id" INT NOT NULL REFERENCES "properties_property" ("id") ON DELETE CASCADE,"feature_id" INT NOT NULL REFERENCES "properties_feature" ("id") ON DELETE CASCADE);
-- downgrade --
DROP TABLE IF EXISTS "properties_feature_property_through";
DROP TABLE IF EXISTS "properties_feature";
