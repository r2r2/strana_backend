-- upgrade --
ALTER TABLE "agencies_agency" ADD "general_type_id" INT;
CREATE TABLE IF NOT EXISTS "agencies_agency_general_type" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "sort" INT NOT NULL  DEFAULT 0,
    "slug" VARCHAR(20) NOT NULL UNIQUE,
    "label" VARCHAR(40) NOT NULL
);
COMMENT ON COLUMN "agencies_agency"."general_type_id" IS 'Тип агентства';
COMMENT ON COLUMN "agencies_agency_general_type"."id" IS 'ID';
COMMENT ON COLUMN "agencies_agency_general_type"."sort" IS 'Сортировка';
COMMENT ON COLUMN "agencies_agency_general_type"."slug" IS 'Слаг';
COMMENT ON COLUMN "agencies_agency_general_type"."label" IS 'Название типа';
COMMENT ON TABLE "agencies_agency_general_type" IS 'Модель типа агентства (агрегатор/АН).';;
ALTER TABLE "agencies_agency" ADD CONSTRAINT "fk_agencies_agencies_8f2260e8" FOREIGN KEY ("general_type_id") REFERENCES "agencies_agency_general_type" ("id") ON DELETE SET NULL;
INSERT INTO "agencies_agency_general_type" (sort, slug, label)
VALUES
    (0, 'agency', 'Агентство'),
    (1, 'aggregator', 'Агрегатор');
UPDATE agencies_agency
SET general_type_id = (
    SELECT agencies_agency_general_type.id
    FROM agencies_agency_general_type
    WHERE agencies_agency_general_type.slug = 'agency'
);
-- downgrade --
ALTER TABLE "agencies_agency" DROP CONSTRAINT "fk_agencies_agencies_8f2260e8";
ALTER TABLE "agencies_agency" DROP COLUMN "general_type_id";
DROP TABLE IF EXISTS "agencies_agency_general_type";
