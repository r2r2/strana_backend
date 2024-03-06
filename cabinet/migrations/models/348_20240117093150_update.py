from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "privilege_benefit" (
    "title" VARCHAR(250) NOT NULL,
    "slug" VARCHAR(250) NOT NULL  PRIMARY KEY,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "priority" INT NOT NULL  DEFAULT 0,
    "image" VARCHAR(500),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "privilege_benefit"."title" IS 'Название';
COMMENT ON COLUMN "privilege_benefit"."slug" IS 'Slug';
COMMENT ON COLUMN "privilege_benefit"."is_active" IS 'Активность';
COMMENT ON COLUMN "privilege_benefit"."priority" IS 'Приоритет в подкатегории';
COMMENT ON COLUMN "privilege_benefit"."image" IS 'Изображение';
COMMENT ON COLUMN "privilege_benefit"."created_at" IS 'Время создания';
COMMENT ON COLUMN "privilege_benefit"."updated_at" IS 'Время последнего обновления';
COMMENT ON TABLE "privilege_benefit" IS 'Преимущества Программы привилегий';
        CREATE TABLE IF NOT EXISTS "privilege_info" (
    "title" VARCHAR(250) NOT NULL,
    "slug" VARCHAR(250) NOT NULL  PRIMARY KEY,
    "description" TEXT NOT NULL,
    "image" VARCHAR(500),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "privilege_info"."title" IS 'Название';
COMMENT ON COLUMN "privilege_info"."slug" IS 'Slug';
COMMENT ON COLUMN "privilege_info"."description" IS 'Описание';
COMMENT ON COLUMN "privilege_info"."image" IS 'Изображение';
COMMENT ON COLUMN "privilege_info"."created_at" IS 'Время создания';
COMMENT ON COLUMN "privilege_info"."updated_at" IS 'Время последнего обновления';
COMMENT ON TABLE "privilege_info" IS 'Общая информация Программы привилегий';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "privilege_benefit";
        DROP TABLE IF EXISTS "privilege_info";
        """