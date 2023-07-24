-- upgrade --
CREATE TABLE IF NOT EXISTS "menus_menu" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(15) NOT NULL,
    "link" VARCHAR(50) NOT NULL,
    "priority" INT NOT NULL,
    "icon" VARCHAR(300),
    "hide_mobile" BOOL NOT NULL  DEFAULT False
);
COMMENT ON COLUMN "menus_menu"."id" IS 'ID';
COMMENT ON COLUMN "menus_menu"."name" IS 'Название пункта меню';
COMMENT ON COLUMN "menus_menu"."link" IS 'Ссылка пункта меню';
COMMENT ON COLUMN "menus_menu"."priority" IS 'Приоритет (чем меньше чем, тем раньше)';
COMMENT ON COLUMN "menus_menu"."icon" IS 'Файл';
COMMENT ON COLUMN "menus_menu"."hide_mobile" IS 'Скрывать на мобильной версии';
COMMENT ON TABLE "menus_menu" IS 'Фиксирует список пунктов бокового меню. Используется 1 инфоблок по ЛК Брокера и ЛК Клиента';;
CREATE TABLE "menus_menu_roles" ("role_id" INT NOT NULL REFERENCES "users_roles" ("id") ON DELETE CASCADE,"menu_role_id" BIGINT NOT NULL REFERENCES "menus_menu" ("id") ON DELETE CASCADE);
CREATE TABLE "menus_menu_cities" ("city_id" INT NOT NULL REFERENCES "cities_city" ("id") ON DELETE CASCADE,"menu_city_id" BIGINT NOT NULL REFERENCES "menus_menu" ("id") ON DELETE CASCADE);
COMMENT ON TABLE "menus_menu_roles" IS 'Роли';
COMMENT ON TABLE "menus_menu_cities" IS 'Города';
-- downgrade --
DROP TABLE IF EXISTS "menus_menu_roles";
DROP TABLE IF EXISTS "menus_menu_cities";
DROP TABLE IF EXISTS "menus_menu";
