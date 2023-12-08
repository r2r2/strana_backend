from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "mortgage_application_status" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "status_name" TEXT NOT NULL,
    "priority" INT NOT NULL  DEFAULT 0,
    "external_code" TEXT NOT NULL
);
COMMENT ON COLUMN "mortgage_application_status"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_application_status"."status_name" IS 'Названеи статуса';
COMMENT ON COLUMN "mortgage_application_status"."priority" IS 'Приоритет';
COMMENT ON COLUMN "mortgage_application_status"."external_code" IS 'Внешний код';
COMMENT ON TABLE "mortgage_application_status" IS 'Статусы заявки ик от застройщика.';
        CREATE TABLE IF NOT EXISTS "mortgage_form" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "phone" VARCHAR(20) NOT NULL,
    "surname" VARCHAR(100) NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "patronymic" VARCHAR(100) NOT NULL
);
COMMENT ON COLUMN "mortgage_form"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_form"."phone" IS 'Номер телефона';
COMMENT ON COLUMN "mortgage_form"."surname" IS 'Фамилия';
COMMENT ON COLUMN "mortgage_form"."name" IS 'Имя';
COMMENT ON COLUMN "mortgage_form"."patronymic" IS 'Отчество';
COMMENT ON TABLE "mortgage_form" IS 'Форма ик.';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "mortgage_application_status";;
        DROP TABLE IF EXISTS "mortgage_form";"""
