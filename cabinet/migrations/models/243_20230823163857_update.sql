-- upgrade --
CREATE TABLE IF NOT EXISTS "payments_property_price_type" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100),
    "default" BOOL NOT NULL  DEFAULT False,
    "slug" VARCHAR(15)
);
COMMENT ON COLUMN "payments_property_price_type"."id" IS 'ID';
COMMENT ON COLUMN "payments_property_price_type"."name" IS 'Название';
COMMENT ON COLUMN "payments_property_price_type"."default" IS 'Тип по умолчанию';
COMMENT ON COLUMN "payments_property_price_type"."slug" IS 'slug для импорта с портала';
COMMENT ON TABLE "payments_property_price_type" IS 'Цена на объект недвижимости';;

CREATE TABLE IF NOT EXISTS "payments_property_price" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "price" DECIMAL(10,2),
    "price_type_id" INT NOT NULL REFERENCES "payments_property_price_type" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "payments_property_price"."id" IS 'ID';
COMMENT ON COLUMN "payments_property_price"."price" IS 'Цена';
COMMENT ON COLUMN "payments_property_price"."price_type_id" IS 'Тип цены';
COMMENT ON TABLE "payments_property_price" IS 'Цена объекта недвижимости';;

CREATE TABLE IF NOT EXISTS "payments_payment_method" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100)
);
COMMENT ON COLUMN "payments_payment_method"."id" IS 'ID';
COMMENT ON COLUMN "payments_payment_method"."name" IS 'Название';
COMMENT ON TABLE "payments_payment_method" IS 'Способ оплаты';;

ALTER TABLE "properties_property" ADD "property_price_id" INT;
COMMENT ON COLUMN "properties_property"."property_price_id" IS 'Цена';
ALTER TABLE "properties_property" ADD CONSTRAINT "fk_properti_payments_be8c8572" FOREIGN KEY ("property_price_id") REFERENCES "payments_property_price" ("id") ON DELETE SET NULL;

CREATE TABLE IF NOT EXISTS "payments_price_offer_matrix" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100),
    "by_dev" BOOL NOT NULL  DEFAULT False,
    "priority" INT NOT NULL  DEFAULT 0,
    "payment_method_id" INT NOT NULL REFERENCES "payments_payment_method" ("id") ON DELETE CASCADE,
    "price_type_id" INT NOT NULL REFERENCES "payments_property_price_type" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "payments_price_offer_matrix"."id" IS 'ID';
COMMENT ON COLUMN "payments_price_offer_matrix"."name" IS 'Название';
COMMENT ON COLUMN "payments_price_offer_matrix"."by_dev" IS 'Субсидированная ипотека';
COMMENT ON COLUMN "payments_price_offer_matrix"."priority" IS 'Приоритет';
COMMENT ON COLUMN "payments_price_offer_matrix"."payment_method_id" IS 'ИД предложения из ИК';
COMMENT ON COLUMN "payments_price_offer_matrix"."price_type_id" IS 'Тип цены';
COMMENT ON TABLE "payments_price_offer_matrix" IS 'Матрица предложения цены';;
-- downgrade --
ALTER TABLE "properties_property" DROP CONSTRAINT "fk_properti_payments_be8c8572";
ALTER TABLE "properties_property" DROP COLUMN "property_price_id";
DROP TABLE IF EXISTS "payments_payment_method" CASCADE;
DROP TABLE IF EXISTS "payments_property_price" CASCADE;
DROP TABLE IF EXISTS "payments_property_price_type" CASCADE;
DROP TABLE IF EXISTS "payments_price_offer_matrix" CASCADE;
