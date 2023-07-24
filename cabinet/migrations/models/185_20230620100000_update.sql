-- upgrade --
alter table if exists public.mainpage_ticket rename to dashboard_ticket;
alter table if exists public.mainpage_ticket_city_through rename to dashboard_ticket_city_through;

CREATE TABLE IF NOT EXISTS "dashboard_block" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "type" VARCHAR(255),
    "width" INT,
    "title" VARCHAR(255),
    "description" TEXT,
    "image" VARCHAR(500),
    "priority" INT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "dashboard_block"."width" IS 'Ширина блока';
COMMENT ON COLUMN "dashboard_block"."image" IS 'Изображение';
COMMENT ON COLUMN "dashboard_block"."priority" IS 'Приоритет';
COMMENT ON COLUMN "dashboard_block"."created_at" IS 'Время создания';
COMMENT ON COLUMN "dashboard_block"."updated_at" IS 'Время последнего обновления';
COMMENT ON TABLE "dashboard_block" IS 'Блок';;
CREATE TABLE IF NOT EXISTS "dashboard_block_city_through" ("city_id" INT NOT NULL REFERENCES "cities_city" ("id") ON DELETE CASCADE,"block_id" INT NOT NULL REFERENCES "dashboard_block" ("id") ON DELETE CASCADE);
COMMENT ON TABLE "dashboard_block_city_through" IS 'Город';

CREATE TABLE IF NOT EXISTS "dashboard_element" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "type" VARCHAR(255) NOT NULL,
    "width" INT,
    "title" VARCHAR(255),
    "description" TEXT,
    "image" VARCHAR(500),
    "expires" TIMESTAMPTZ,
    "has_completed_booking" BOOL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "block_id" INT REFERENCES "dashboard_block" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "dashboard_element"."width" IS 'Ширина блока';
COMMENT ON COLUMN "dashboard_element"."image" IS 'Изображение';
COMMENT ON COLUMN "dashboard_element"."expires" IS 'Время истечения';
COMMENT ON COLUMN "dashboard_element"."has_completed_booking" IS 'Бронирование завершено';
COMMENT ON COLUMN "dashboard_element"."created_at" IS 'Время создания';
COMMENT ON COLUMN "dashboard_element"."updated_at" IS 'Время последнего обновления';
COMMENT ON COLUMN "dashboard_element"."block_id" IS 'Блок';
COMMENT ON TABLE "dashboard_element" IS 'Элемент';;

CREATE TABLE IF NOT EXISTS "dashboard_link" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "link" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "element_id" INT REFERENCES "dashboard_element" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "dashboard_link"."link" IS 'Ссылка';
COMMENT ON COLUMN "dashboard_link"."created_at" IS 'Время создания';
COMMENT ON COLUMN "dashboard_link"."updated_at" IS 'Время последнего обновления';
COMMENT ON COLUMN "dashboard_link"."element_id" IS 'Элемент';
COMMENT ON TABLE "dashboard_link" IS 'Ссылка';;
CREATE TABLE IF NOT EXISTS "dashboard_link_city_through" ("city_id" INT NOT NULL REFERENCES "cities_city" ("id") ON DELETE CASCADE,"link_id" INT NOT NULL REFERENCES "dashboard_link" ("id") ON DELETE CASCADE);
COMMENT ON TABLE "dashboard_link_city_through" IS 'Город';
CREATE TABLE IF NOT EXISTS "dashboard_element_city_through" ("city_id" INT NOT NULL REFERENCES "cities_city" ("id") ON DELETE CASCADE,"element_id" INT NOT NULL REFERENCES "dashboard_element" ("id") ON DELETE CASCADE);

-- downgrade --
DROP TABLE IF EXISTS "dashboard_block" CASCADE;
DROP TABLE IF EXISTS "dashboard_block_city_through";
DROP TABLE IF EXISTS "dashboard_element" CASCADE;
DROP TABLE IF EXISTS "dashboard_element_city_through";
DROP TABLE IF EXISTS "dashboard_link" CASCADE;
DROP TABLE IF EXISTS "dashboard_link_city_through";
