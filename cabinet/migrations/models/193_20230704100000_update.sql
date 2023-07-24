-- upgrade --
CREATE TABLE IF NOT EXISTS "users_unique_statuses" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "subtitle" VARCHAR(255),
    "icon" VARCHAR(36) NOT NULL,
    "text_color" VARCHAR(7)   DEFAULT '#8F00FF',
    "background_color" VARCHAR(7)   DEFAULT '#8F00FF',
    "slug" VARCHAR(255),
    "style_list" VARCHAR(36),
    "type" VARCHAR(36),
    "comment" TEXT
);
COMMENT ON COLUMN "users_unique_statuses"."id" IS 'ID';
COMMENT ON COLUMN "users_unique_statuses"."title" IS 'Заголовок';
COMMENT ON COLUMN "users_unique_statuses"."subtitle" IS 'Подзаголовок';
COMMENT ON COLUMN "users_unique_statuses"."icon" IS 'Иконка';
COMMENT ON COLUMN "users_unique_statuses"."text_color" IS 'Цвет текста';
COMMENT ON COLUMN "users_unique_statuses"."background_color" IS 'Цвет фона';
COMMENT ON COLUMN "users_unique_statuses"."slug" IS 'Слаг';
COMMENT ON COLUMN "users_unique_statuses"."style_list" IS 'Стиль в списке';
COMMENT ON COLUMN "users_unique_statuses"."type" IS 'Тип';
COMMENT ON COLUMN "users_unique_statuses"."comment" IS 'Комментарий';
COMMENT ON TABLE "users_unique_statuses" IS 'Таблица статусов уникальности';
-- downgrade --
DROP TABLE IF EXISTS "users_unique_statuses";
