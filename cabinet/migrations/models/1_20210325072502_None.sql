-- upgrade --
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "users_user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(100)  UNIQUE,
    "password" VARCHAR(200),
    "email" VARCHAR(100)  UNIQUE,
    "phone" VARCHAR(20)  UNIQUE,
    "code" VARCHAR(4),
    "code_time" TIMESTAMPTZ,
    "token" UUID,
    "name" VARCHAR(50),
    "surname" VARCHAR(50),
    "patronymic" VARCHAR(50),
    "birth_date" DATE,
    "is_active" BOOL NOT NULL  DEFAULT False,
    "is_superuser" BOOL NOT NULL  DEFAULT False
);
COMMENT ON COLUMN "users_user"."id" IS 'ID';
COMMENT ON COLUMN "users_user"."username" IS 'Имя пользователя';
COMMENT ON COLUMN "users_user"."password" IS 'Пароль';
COMMENT ON COLUMN "users_user"."email" IS 'Email';
COMMENT ON COLUMN "users_user"."phone" IS 'Номер телефона';
COMMENT ON COLUMN "users_user"."code" IS 'Код';
COMMENT ON COLUMN "users_user"."code_time" IS 'Время отправки кода';
COMMENT ON COLUMN "users_user"."token" IS 'Токен';
COMMENT ON COLUMN "users_user"."name" IS 'Имя';
COMMENT ON COLUMN "users_user"."surname" IS 'Фамилия';
COMMENT ON COLUMN "users_user"."patronymic" IS 'Отчество';
COMMENT ON COLUMN "users_user"."birth_date" IS 'Дата рождения';
COMMENT ON COLUMN "users_user"."is_active" IS 'Активный';
COMMENT ON COLUMN "users_user"."is_superuser" IS 'Супер пользователь';
COMMENT ON TABLE "users_user" IS 'Пользователь';
CREATE TABLE IF NOT EXISTS "documents_document" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text" TEXT NOT NULL,
    "slug" VARCHAR(50) NOT NULL
);
COMMENT ON COLUMN "documents_document"."id" IS 'ID';
COMMENT ON COLUMN "documents_document"."text" IS 'Текст';
COMMENT ON COLUMN "documents_document"."slug" IS 'Слаг';
COMMENT ON TABLE "documents_document" IS 'Документ';
CREATE TABLE IF NOT EXISTS "projects_project" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "global_id" VARCHAR(200)  UNIQUE,
    "name" VARCHAR(200),
    "city" VARCHAR(100)
);
COMMENT ON COLUMN "projects_project"."id" IS 'ID';
COMMENT ON COLUMN "projects_project"."global_id" IS 'Глобальный ID';
COMMENT ON COLUMN "projects_project"."name" IS 'Имя';
COMMENT ON COLUMN "projects_project"."city" IS 'Город';
COMMENT ON TABLE "projects_project" IS 'Проект';
CREATE TABLE IF NOT EXISTS "buildings_building" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "global_id" VARCHAR(200)  UNIQUE,
    "name" VARCHAR(100),
    "built_year" INT,
    "ready_quarter" INT,
    "booking_active" BOOL NOT NULL  DEFAULT True,
    "booking_period" INT,
    "booking_price" INT,
    "project_id" INT REFERENCES "projects_project" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "buildings_building"."id" IS 'ID';
COMMENT ON COLUMN "buildings_building"."global_id" IS 'Глобальный ID';
COMMENT ON COLUMN "buildings_building"."name" IS 'Имя';
COMMENT ON COLUMN "buildings_building"."built_year" IS 'Год постройки';
COMMENT ON COLUMN "buildings_building"."ready_quarter" IS 'Квартал готовности';
COMMENT ON COLUMN "buildings_building"."booking_active" IS 'Бронирование активно';
COMMENT ON COLUMN "buildings_building"."booking_period" IS 'Период бронирования';
COMMENT ON COLUMN "buildings_building"."booking_price" IS 'Стоимость бронирования';
COMMENT ON COLUMN "buildings_building"."project_id" IS 'Проект';
COMMENT ON TABLE "buildings_building" IS 'Корпус';
CREATE TABLE IF NOT EXISTS "floors_floor" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "global_id" VARCHAR(200)  UNIQUE,
    "number" VARCHAR(20),
    "building_id" INT REFERENCES "buildings_building" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "floors_floor"."id" IS 'ID';
COMMENT ON COLUMN "floors_floor"."global_id" IS 'Глобальный ID';
COMMENT ON COLUMN "floors_floor"."number" IS 'Номер';
COMMENT ON COLUMN "floors_floor"."building_id" IS 'Корпус';
COMMENT ON TABLE "floors_floor" IS 'Этаж';
CREATE TABLE IF NOT EXISTS "properties_property" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "global_id" VARCHAR(200)  UNIQUE,
    "type" VARCHAR(50),
    "article" VARCHAR(50),
    "plan" VARCHAR(300),
    "plan_png" VARCHAR(300),
    "price" BIGINT,
    "original_price" BIGINT,
    "area" DECIMAL(7,2),
    "deadline" VARCHAR(50),
    "discount" BIGINT,
    "project_id" INT REFERENCES "projects_project" ("id") ON DELETE CASCADE,
    "floor_id" INT REFERENCES "floors_floor" ("id") ON DELETE CASCADE,
    "building_id" INT REFERENCES "buildings_building" ("id") ON DELETE CASCADE,
    "user_id" INT REFERENCES "users_user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "properties_property"."id" IS 'ID';
COMMENT ON COLUMN "properties_property"."global_id" IS 'Глобальный ID';
COMMENT ON COLUMN "properties_property"."type" IS 'Тип';
COMMENT ON COLUMN "properties_property"."article" IS 'Артикул';
COMMENT ON COLUMN "properties_property"."plan" IS 'Планировка';
COMMENT ON COLUMN "properties_property"."plan_png" IS 'Планировка png';
COMMENT ON COLUMN "properties_property"."price" IS 'Цена';
COMMENT ON COLUMN "properties_property"."original_price" IS 'Оригинальная цена';
COMMENT ON COLUMN "properties_property"."area" IS 'Площадь';
COMMENT ON COLUMN "properties_property"."deadline" IS 'Срок сдачи';
COMMENT ON COLUMN "properties_property"."discount" IS 'Скидка';
COMMENT ON COLUMN "properties_property"."project_id" IS 'Проект';
COMMENT ON COLUMN "properties_property"."floor_id" IS 'Этаж';
COMMENT ON COLUMN "properties_property"."building_id" IS 'Корпус';
COMMENT ON COLUMN "properties_property"."user_id" IS 'Пользователь';
COMMENT ON TABLE "properties_property" IS 'Объект недвижимости';
