from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "news_news" (
            "id" BIGSERIAL NOT NULL PRIMARY KEY,
            "title" VARCHAR(150) NOT NULL,
            "slug" VARCHAR(100) NOT NULL UNIQUE,
            "short_description" TEXT,
            "description" TEXT,
            "is_active" BOOL NOT NULL  DEFAULT True,
            "image_preview" VARCHAR(500),
            "image" VARCHAR(500),
            "pub_date" TIMESTAMPTZ,
            "end_date" TIMESTAMPTZ,
            "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
        );
        COMMENT ON COLUMN "news_news"."id" IS 'ID';
        COMMENT ON COLUMN "news_news"."title" IS 'Заголовок новости';
        COMMENT ON COLUMN "news_news"."slug" IS 'Слаг новости';
        COMMENT ON COLUMN "news_news"."short_description" IS 'Краткое описание новости';
        COMMENT ON COLUMN "news_news"."description" IS 'Описание новости';
        COMMENT ON COLUMN "news_news"."is_active" IS 'Новость активна';
        COMMENT ON COLUMN "news_news"."image_preview" IS 'Изображение (превью)';
        COMMENT ON COLUMN "news_news"."image" IS 'Изображение';
        COMMENT ON COLUMN "news_news"."pub_date" IS 'Дата публикации новости';
        COMMENT ON COLUMN "news_news"."end_date" IS 'Дата окончания новости';
        COMMENT ON COLUMN "news_news"."created_at" IS 'Время создания';
        COMMENT ON COLUMN "news_news"."updated_at" IS 'Время обновления';
        COMMENT ON TABLE "news_news" IS 'Новости.';
        
        CREATE TABLE IF NOT EXISTS "news_news_tag" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "label" VARCHAR(100) NOT NULL,
            "slug" VARCHAR(100) NOT NULL UNIQUE,
            "is_active" BOOL NOT NULL  DEFAULT True,
            "priority" INT NOT NULL  DEFAULT 0
        );
        COMMENT ON COLUMN "news_news_tag"."id" IS 'ID';
        COMMENT ON COLUMN "news_news_tag"."label" IS 'Название тега';
        COMMENT ON COLUMN "news_news_tag"."slug" IS 'Слаг тега';
        COMMENT ON COLUMN "news_news_tag"."is_active" IS 'Активность';
        COMMENT ON COLUMN "news_news_tag"."priority" IS 'Приоритет';
        COMMENT ON TABLE "news_news_tag" IS 'Теги новостей.';
        
        CREATE TABLE IF NOT EXISTS "news_news_tag_through" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "news_id" BIGINT NOT NULL REFERENCES "news_news" ("id") ON DELETE CASCADE,
            "news_tag_id" INT NOT NULL REFERENCES "news_news_tag" ("id") ON DELETE CASCADE
        );
        COMMENT ON COLUMN "news_news_tag_through"."news_id" IS 'Новость';
        COMMENT ON COLUMN "news_news_tag_through"."news_tag_id" IS 'Тег';
        COMMENT ON TABLE "news_news_tag_through" IS 'Выбранные теги для новостей.';
        
        CREATE TABLE IF NOT EXISTS "news_news_user_role_through" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "news_id" BIGINT NOT NULL REFERENCES "news_news" ("id") ON DELETE CASCADE,
            "role_id" INT NOT NULL REFERENCES "users_roles" ("id") ON DELETE CASCADE
        );
        COMMENT ON COLUMN "news_news_user_role_through"."news_id" IS 'Новость';
        COMMENT ON COLUMN "news_news_user_role_through"."role_id" IS 'Роль пользователя';
        COMMENT ON TABLE "news_news_user_role_through" IS 'Выбранные роли пользователей для новостей.';
        
        CREATE TABLE IF NOT EXISTS "news_news_project_through" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "news_id" BIGINT NOT NULL REFERENCES "news_news" ("id") ON DELETE CASCADE,
            "project_id" INT NOT NULL REFERENCES "projects_project" ("id") ON DELETE CASCADE
        );
        COMMENT ON COLUMN "news_news_project_through"."news_id" IS 'Новость';
        COMMENT ON COLUMN "news_news_project_through"."project_id" IS 'Проект';
        COMMENT ON TABLE "news_news_project_through" IS 'Выбранные проекты для новостей.';
        
        CREATE TABLE IF NOT EXISTS "news_news_viewed_info" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "viewing_date" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
            "is_voice_left" BOOL NOT NULL  DEFAULT False,
            "is_useful" BOOL NOT NULL  DEFAULT False,
            "news_id" BIGINT REFERENCES "news_news" ("id") ON DELETE SET NULL,
            "user_id" INT REFERENCES "users_user" ("id") ON DELETE CASCADE
        );
        COMMENT ON COLUMN "news_news_viewed_info"."id" IS 'ID';
        COMMENT ON COLUMN "news_news_viewed_info"."viewing_date" IS 'Дата и время просмотра';
        COMMENT ON COLUMN "news_news_viewed_info"."is_voice_left" IS 'Пользователь проголосовал под новостью';
        COMMENT ON COLUMN "news_news_viewed_info"."is_useful" IS 'Новость была полезной';
        COMMENT ON COLUMN "news_news_viewed_info"."news_id" IS 'Новость';
        COMMENT ON COLUMN "news_news_viewed_info"."user_id" IS 'Пользователь';
        COMMENT ON TABLE "news_news_viewed_info" IS 'Просмотренные новости.';
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "news_news_user_role_through";
        DROP TABLE IF EXISTS "news_news_project_through";
        DROP TABLE IF EXISTS "news_news_tag_through";
        DROP TABLE IF EXISTS "news_news_viewed_info";
        DROP TABLE IF EXISTS "news_news_tag";
        DROP TABLE IF EXISTS "news_news";
        """
