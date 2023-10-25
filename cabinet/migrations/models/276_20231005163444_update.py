from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "notifications_email_headers" (
            "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
            "id" SERIAL NOT NULL PRIMARY KEY,
            "text" TEXT NOT NULL,
            "description" TEXT,
            "slug" VARCHAR(100) NOT NULL  UNIQUE,
            "is_active" BOOL NOT NULL  DEFAULT True
        );
        COMMENT ON COLUMN "notifications_email_headers"."created_at" IS 'Когда создано';
        COMMENT ON COLUMN "notifications_email_headers"."updated_at" IS 'Когда обновлено';
        COMMENT ON COLUMN "notifications_email_headers"."id" IS 'ID';
        COMMENT ON COLUMN "notifications_email_headers"."text" IS 'Текст шаблона хэдера письма';
        COMMENT ON COLUMN "notifications_email_headers"."description" IS 'Описание назначения шаблона хэдера письма';
        COMMENT ON COLUMN "notifications_email_headers"."slug" IS 'Слаг шаблона хэдера письма';
        COMMENT ON COLUMN "notifications_email_headers"."is_active" IS 'Шаблон хэдера письма активен';
        COMMENT ON TABLE "notifications_email_headers" IS 'Шаблоны хэдеров писем.';
        
        CREATE TABLE IF NOT EXISTS "notifications_email_footers" (
            "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
            "id" SERIAL NOT NULL PRIMARY KEY,
            "text" TEXT NOT NULL,
            "description" TEXT,
            "slug" VARCHAR(100) NOT NULL  UNIQUE,
            "is_active" BOOL NOT NULL  DEFAULT True
        );
        COMMENT ON COLUMN "notifications_email_footers"."created_at" IS 'Когда создано';
        COMMENT ON COLUMN "notifications_email_footers"."updated_at" IS 'Когда обновлено';
        COMMENT ON COLUMN "notifications_email_footers"."id" IS 'ID';
        COMMENT ON COLUMN "notifications_email_footers"."text" IS 'Текст шаблона футера письма';
        COMMENT ON COLUMN "notifications_email_footers"."description" IS 'Описание назначения шаблона футера письма';
        COMMENT ON COLUMN "notifications_email_footers"."slug" IS 'Слаг шаблона футера письма';
        COMMENT ON COLUMN "notifications_email_footers"."is_active" IS 'Шаблон футера письма активен';
        COMMENT ON TABLE "notifications_email_footers" IS 'Шаблоны футеров писем.';
    
        ALTER TABLE "notifications_email_notification" ADD "header_template_id" INT;
        ALTER TABLE "notifications_email_notification" ADD "footer_template_id" INT;
        ALTER TABLE "notifications_email_notification" ADD CONSTRAINT "fk_notifica_notifica_72344077" FOREIGN KEY ("header_template_id") REFERENCES "notifications_email_headers" ("id") ON DELETE CASCADE;
        ALTER TABLE "notifications_email_notification" ADD CONSTRAINT "fk_notifica_notifica_4119bb16" FOREIGN KEY ("footer_template_id") REFERENCES "notifications_email_footers" ("id") ON DELETE CASCADE;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "notifications_email_notification" DROP CONSTRAINT "fk_notifica_notifica_4119bb16";
        ALTER TABLE "notifications_email_notification" DROP CONSTRAINT "fk_notifica_notifica_72344077";
        ALTER TABLE "notifications_email_notification" DROP COLUMN "header_template_id";
        ALTER TABLE "notifications_email_notification" DROP COLUMN "footer_template_id";
        DROP TABLE IF EXISTS "notifications_email_headers";
        DROP TABLE IF EXISTS "notifications_email_headers";"""
