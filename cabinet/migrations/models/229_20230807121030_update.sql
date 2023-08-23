-- upgrade --
CREATE TABLE IF NOT EXISTS "properties_property_type" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "sort" INT NOT NULL  DEFAULT 0,
    "slug" VARCHAR(20) NOT NULL UNIQUE,
    "label" VARCHAR(40) NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True
);
COMMENT ON COLUMN "properties_property_type"."id" IS 'ID';
COMMENT ON COLUMN "properties_property_type"."sort" IS 'Приоритет';
COMMENT ON COLUMN "properties_property_type"."slug" IS 'Слаг';
COMMENT ON COLUMN "properties_property_type"."label" IS 'Название типа';
COMMENT ON COLUMN "properties_property_type"."is_active" IS 'Активность';
COMMENT ON TABLE "properties_property_type" IS 'Модель типа объектов недвижимости.';
INSERT INTO "properties_property_type" (sort, slug, label)
VALUES
    (0, 'flat', 'Квартира'),
    (1, 'parking', 'Паркинг'),
    (2, 'commercial', 'Коммерция'),
    (3, 'pantry', 'Кладовка'),
    (4, 'commercial_apartment', 'Апартаменты коммерции');

CREATE TABLE "properties_property_type_pipelines" ("property_type_id" INT NOT NULL REFERENCES "properties_property_type" ("id") ON DELETE CASCADE,"pipeline_id" INT NOT NULL REFERENCES "amocrm_pipelines" ("id") ON DELETE CASCADE);
ALTER TABLE "properties_property" ADD "property_type_id" INT;
ALTER TABLE "properties_property" ADD CONSTRAINT "fk_properti_properti_b6d1ed14" FOREIGN KEY ("property_type_id") REFERENCES "properties_property_type" ("id") ON DELETE SET NULL;

UPDATE properties_property
SET property_type_id = (
    SELECT properties_property_type.id
    FROM properties_property_type
    WHERE UPPER(properties_property_type.slug) = properties_property.type
);
-- downgrade --
ALTER TABLE "properties_property" DROP CONSTRAINT "fk_properti_properti_b6d1ed14";
ALTER TABLE "properties_property" DROP COLUMN "property_type_id";
DROP TABLE IF EXISTS "properties_property_type_pipelines";
DROP TABLE IF EXISTS "properties_property_type";


