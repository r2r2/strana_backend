from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "documents_interaction" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(150) NOT NULL,
    "icon" VARCHAR(350),
    "file" VARCHAR(350),
    "priority" INT NOT NULL
);
COMMENT ON COLUMN "documents_interaction"."id" IS 'ID';
COMMENT ON COLUMN "documents_interaction"."name" IS 'Имя взаимодействия';
COMMENT ON COLUMN "documents_interaction"."icon" IS 'Ссылка на иконку';
COMMENT ON COLUMN "documents_interaction"."file" IS 'Ссылка на файл';
COMMENT ON COLUMN "documents_interaction"."priority" IS 'Приоритет взаимодействия';
COMMENT ON TABLE "documents_interaction" IS 'Взаимодейтвие';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "documents_interaction";"""
