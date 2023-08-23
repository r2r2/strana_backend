-- upgrade --
CREATE TABLE IF NOT EXISTS "main_page_content" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text" TEXT NOT NULL,
    "slug" VARCHAR(50) NOT NULL,
    "comment" TEXT NOT NULL
);
COMMENT ON COLUMN "main_page_content"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "main_page_content"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "main_page_content"."id" IS 'ID';
COMMENT ON COLUMN "main_page_content"."text" IS 'Текст главной страницы';
COMMENT ON COLUMN "main_page_content"."slug" IS 'Slug';
COMMENT ON COLUMN "main_page_content"."comment" IS 'Внутренний комментарий';
COMMENT ON TABLE "main_page_content" IS 'Контент и заголовки главной страницы';;
CREATE TABLE IF NOT EXISTS "main_page_manager" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "manager_id" BIGINT NOT NULL REFERENCES "users_managers" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "main_page_manager"."id" IS 'ID';
COMMENT ON COLUMN "main_page_manager"."manager_id" IS 'Менеджер';
COMMENT ON TABLE "main_page_manager" IS 'Блок: Продавайте online';;
CREATE TABLE IF NOT EXISTS "main_page_offer" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "image" VARCHAR(500),
    "priority" INT,
    "is_active" BOOL NOT NULL  DEFAULT True
);
COMMENT ON COLUMN "main_page_offer"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "main_page_offer"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "main_page_offer"."id" IS 'ID';
COMMENT ON COLUMN "main_page_offer"."title" IS 'Заголовок';
COMMENT ON COLUMN "main_page_offer"."description" IS 'Описание';
COMMENT ON COLUMN "main_page_offer"."image" IS 'Изображение';
COMMENT ON COLUMN "main_page_offer"."priority" IS 'Приоритет';
COMMENT ON COLUMN "main_page_offer"."is_active" IS 'Активность';
COMMENT ON TABLE "main_page_offer" IS 'Блок: что мы предлагаем';;
CREATE TABLE IF NOT EXISTS "main_page_partner_logo" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "image" VARCHAR(500),
    "priority" INT,
    "is_active" BOOL NOT NULL  DEFAULT True
);
COMMENT ON COLUMN "main_page_partner_logo"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "main_page_partner_logo"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "main_page_partner_logo"."id" IS 'ID';
COMMENT ON COLUMN "main_page_partner_logo"."image" IS 'Изображение';
COMMENT ON COLUMN "main_page_partner_logo"."priority" IS 'Приоритет';
COMMENT ON COLUMN "main_page_partner_logo"."is_active" IS 'Активность';
COMMENT ON TABLE "main_page_partner_logo" IS 'Блок: логотипы партнеров';;
CREATE TABLE IF NOT EXISTS "main_page_sell_online" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "priority" INT,
    "is_active" BOOL NOT NULL  DEFAULT True
);
COMMENT ON COLUMN "main_page_sell_online"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "main_page_sell_online"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "main_page_sell_online"."id" IS 'ID';
COMMENT ON COLUMN "main_page_sell_online"."title" IS 'Заголовок';
COMMENT ON COLUMN "main_page_sell_online"."description" IS 'Описание';
COMMENT ON COLUMN "main_page_sell_online"."priority" IS 'Приоритет';
COMMENT ON COLUMN "main_page_sell_online"."is_active" IS 'Активность';
COMMENT ON TABLE "main_page_sell_online" IS 'Блок: Продавайте online';-- downgrade --
DROP TABLE IF EXISTS "main_page_content";
DROP TABLE IF EXISTS "main_page_manager";
DROP TABLE IF EXISTS "main_page_offer";
DROP TABLE IF EXISTS "main_page_partner_logo";
DROP TABLE IF EXISTS "main_page_sell_online";
