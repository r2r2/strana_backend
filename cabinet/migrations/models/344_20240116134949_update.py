from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "privilege_category" (
    "slug" VARCHAR(250) NOT NULL  PRIMARY KEY,
    "title" VARCHAR(250) NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "dashboard_priority" INT NOT NULL  DEFAULT 0,
    "filter_priority" INT NOT NULL  DEFAULT 0,
    "image" VARCHAR(500),
    "display_type" VARCHAR(250),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
        CREATE TABLE "privilege_category_m2m_city" (
    "city_id" INT NOT NULL REFERENCES "cities_city" ("id") ON DELETE CASCADE,
    "privilege_category_id" VARCHAR(250) NOT NULL REFERENCES "privilege_category" ("slug") ON DELETE CASCADE
);
COMMENT ON TABLE "privilege_category_m2m_city" IS 'Города';
COMMENT ON COLUMN "privilege_category"."slug" IS 'Slug';
COMMENT ON COLUMN "privilege_category"."title" IS 'Название';
COMMENT ON COLUMN "privilege_category"."is_active" IS 'Активность';
COMMENT ON COLUMN "privilege_category"."dashboard_priority" IS 'Приоритет на дашборде';
COMMENT ON COLUMN "privilege_category"."filter_priority" IS 'Приоритет в фильтре';
COMMENT ON COLUMN "privilege_category"."image" IS 'Изображение';
COMMENT ON COLUMN "privilege_category"."created_at" IS 'Время создания';
COMMENT ON COLUMN "privilege_category"."updated_at" IS 'Время последнего обновления';
COMMENT ON TABLE "privilege_category" IS 'Категория программ привилегий';

        CREATE TABLE IF NOT EXISTS "privilege_subcategory" (
    "slug" VARCHAR(250) NOT NULL  PRIMARY KEY,
    "title" VARCHAR(250) NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "category_id" VARCHAR(250) REFERENCES "privilege_category" ("slug") ON DELETE CASCADE
);
COMMENT ON COLUMN "privilege_subcategory"."slug" IS 'Слаг';
COMMENT ON COLUMN "privilege_subcategory"."title" IS 'Название';
COMMENT ON COLUMN "privilege_subcategory"."is_active" IS 'Активность';
COMMENT ON COLUMN "privilege_subcategory"."created_at" IS 'Время создания';
COMMENT ON COLUMN "privilege_subcategory"."updated_at" IS 'Время последнего обновления';
COMMENT ON TABLE "privilege_subcategory" IS 'Подкатегория программ привилегий';
        CREATE TABLE IF NOT EXISTS "privilege_cooperation_type" (
    "slug" VARCHAR(250) NOT NULL  PRIMARY KEY,
    "title" VARCHAR(250) NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "privilege_cooperation_type"."slug" IS 'Slug';
COMMENT ON COLUMN "privilege_cooperation_type"."title" IS 'Название';
COMMENT ON COLUMN "privilege_cooperation_type"."is_active" IS 'Активность';
COMMENT ON COLUMN "privilege_cooperation_type"."created_at" IS 'Время создания';
COMMENT ON COLUMN "privilege_cooperation_type"."updated_at" IS 'Время последнего обновления';
COMMENT ON TABLE "privilege_cooperation_type" IS 'Виды сотрудничества программы привилегий';
        CREATE TABLE IF NOT EXISTS "privilege_company" (
    "title" VARCHAR(250) NOT NULL,
    "slug" VARCHAR(250) NOT NULL  PRIMARY KEY,
    "description" TEXT NOT NULL,
    "link" VARCHAR(250) NOT NULL,
    "image" VARCHAR(500),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "privilege_company"."title" IS 'Название';
COMMENT ON COLUMN "privilege_company"."slug" IS 'Slug';
COMMENT ON COLUMN "privilege_company"."description" IS 'Описание';
COMMENT ON COLUMN "privilege_company"."link" IS 'Ссылка на сайт';
COMMENT ON COLUMN "privilege_company"."image" IS 'Изображение';
COMMENT ON COLUMN "privilege_company"."created_at" IS 'Время создания';
COMMENT ON COLUMN "privilege_company"."updated_at" IS 'Время последнего обновления';
COMMENT ON TABLE "privilege_company" IS 'Компания-Партнёр программы привилегий';
        CREATE TABLE IF NOT EXISTS "privilege_program" (
    "slug" VARCHAR(250) NOT NULL  PRIMARY KEY,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "priority_in_subcategory" INT NOT NULL  DEFAULT 0,
    "until" DOUBLE PRECISION,
    "description" TEXT NOT NULL,
    "conditions" TEXT NOT NULL,
    "promocode" VARCHAR(250) NOT NULL,
    "promocode_rules" TEXT NOT NULL,
    "button_label" VARCHAR(250) NOT NULL,
    "button_link" VARCHAR(250) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "category_id" VARCHAR(250) REFERENCES "privilege_category" ("slug") ON DELETE SET NULL,
    "cooperation_type_id" VARCHAR(250) REFERENCES "privilege_cooperation_type" ("slug") ON DELETE SET NULL,
    "partner_company_id" VARCHAR(250) NOT NULL REFERENCES "privilege_company" ("slug") ON DELETE CASCADE,
    "subcategory_id" VARCHAR(250) REFERENCES "privilege_subcategory" ("slug") ON DELETE SET NULL
);
COMMENT ON COLUMN "privilege_program"."slug" IS 'Slug';
COMMENT ON COLUMN "privilege_program"."is_active" IS 'Активность';
COMMENT ON COLUMN "privilege_program"."priority_in_subcategory" IS 'Приоритет в подкатегории';
COMMENT ON COLUMN "privilege_program"."until" IS 'Срок действия';
COMMENT ON COLUMN "privilege_program"."description" IS 'Краткое описание';
COMMENT ON COLUMN "privilege_program"."conditions" IS 'Условия';
COMMENT ON COLUMN "privilege_program"."promocode" IS 'Промокод';
COMMENT ON COLUMN "privilege_program"."promocode_rules" IS 'Правила использования промокода';
COMMENT ON COLUMN "privilege_program"."button_label" IS 'Название кнопки';
COMMENT ON COLUMN "privilege_program"."button_link" IS 'Ссылка на кнопке';
COMMENT ON COLUMN "privilege_program"."created_at" IS 'Время создания';
COMMENT ON COLUMN "privilege_program"."updated_at" IS 'Время последнего обновления';
COMMENT ON COLUMN "privilege_program"."cooperation_type_id" IS 'Вид сотрудничества';
COMMENT ON COLUMN "privilege_program"."partner_company_id" IS 'Компания-партнёр';
COMMENT ON TABLE "privilege_program" IS 'Программа привилегий';
        CREATE TABLE IF NOT EXISTS "privilege_request" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "full_name" VARCHAR(150) NOT NULL,
    "phone" VARCHAR(20) NOT NULL,
    "email" VARCHAR(100) NOT NULL,
    "question" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_privilege_r_phone_b69f5f" ON "privilege_request" ("phone");
COMMENT ON COLUMN "privilege_request"."id" IS 'ID';
COMMENT ON COLUMN "privilege_request"."full_name" IS 'ФИО клиента';
COMMENT ON COLUMN "privilege_request"."phone" IS 'Номер телефона';
COMMENT ON COLUMN "privilege_request"."email" IS 'Email';
COMMENT ON COLUMN "privilege_request"."question" IS 'Вопрос';
COMMENT ON COLUMN "privilege_request"."created_at" IS 'Время создания';
COMMENT ON COLUMN "privilege_request"."updated_at" IS 'Время последнего обновления';
COMMENT ON TABLE "privilege_request" IS 'Запрос в Программу привилегий';
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "privilege_program";
        DROP TABLE IF EXISTS "privilege_subcategory";
        DROP TABLE IF EXISTS "privilege_category_m2m_city";
        DROP TABLE IF EXISTS "privilege_category";
        DROP TABLE IF EXISTS "privilege_cooperation_type";
        DROP TABLE IF EXISTS "privilege_company";
        DROP TABLE IF EXISTS "privilege_request";
        """
