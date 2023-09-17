from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "additional_services_condition" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(150) NOT NULL
);
COMMENT ON COLUMN "additional_services_condition"."id" IS 'ID';
COMMENT ON COLUMN "additional_services_condition"."title" IS 'Название';
COMMENT ON TABLE "additional_services_condition" IS 'Модель \"Как получить услугу\"';

        CREATE TABLE IF NOT EXISTS "additional_services_condition_step" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "priority" INT NOT NULL  DEFAULT 0,
    "description" TEXT NOT NULL,
    "active" BOOL NOT NULL  DEFAULT True,
    "condition_id" INT REFERENCES "additional_services_condition" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "additional_services_condition_step"."id" IS 'ID';
COMMENT ON COLUMN "additional_services_condition_step"."priority" IS 'Приоритет';
COMMENT ON COLUMN "additional_services_condition_step"."description" IS 'Текст описания';
COMMENT ON COLUMN "additional_services_condition_step"."active" IS 'Активность';
COMMENT ON TABLE "additional_services_condition_step" IS 'Шаг для \"Как получить услугу\"';

        CREATE TABLE IF NOT EXISTS "additional_services_category" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(150) NOT NULL,
    "priority" INT NOT NULL  DEFAULT 0,
    "active" BOOL NOT NULL  DEFAULT True
);
COMMENT ON COLUMN "additional_services_category"."id" IS 'ID';
COMMENT ON COLUMN "additional_services_category"."title" IS 'Название';
COMMENT ON COLUMN "additional_services_category"."priority" IS 'Приоритет';
COMMENT ON COLUMN "additional_services_category"."active" IS 'Активность';
COMMENT ON TABLE "additional_services_category" IS 'Категория (вид) услуги';

        CREATE TABLE IF NOT EXISTS "additional_services_service" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(150) NOT NULL,
    "priority" INT NOT NULL  DEFAULT 0,
    "image_preview" VARCHAR(300),
    "image_detailed" VARCHAR(300),
    "announcement" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "active" BOOL NOT NULL  DEFAULT True,
    "hint" TEXT NOT NULL,
    "category_id" INT REFERENCES "additional_services_category" ("id") ON DELETE SET NULL,
    "condition_id" INT REFERENCES "additional_services_condition" ("id") ON DELETE SET NULL,
    "group_status_id" INT REFERENCES "amocrm_group_statuses" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "additional_services_service"."id" IS 'ID';
COMMENT ON COLUMN "additional_services_service"."title" IS 'Название';
COMMENT ON COLUMN "additional_services_service"."priority" IS 'Приоритет';
COMMENT ON COLUMN "additional_services_service"."image_preview" IS 'Превью изображения';
COMMENT ON COLUMN "additional_services_service"."image_detailed" IS 'Детальное изображение';
COMMENT ON COLUMN "additional_services_service"."announcement" IS 'Анонс';
COMMENT ON COLUMN "additional_services_service"."description" IS 'Подробная информация';
COMMENT ON COLUMN "additional_services_service"."active" IS 'Активность';
COMMENT ON COLUMN "additional_services_service"."hint" IS 'Текст подсказки';
COMMENT ON TABLE "additional_services_service" IS 'Доп услуга';


        CREATE TABLE IF NOT EXISTS "additional_services_ticket" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "cost" DECIMAL(15,2),
    "full_name" VARCHAR(150) NOT NULL,
    "phone" VARCHAR(20) NOT NULL,
    "booking_id" INT REFERENCES "booking_booking" ("id") ON DELETE SET NULL,
    "service_id" INT REFERENCES "additional_services_service" ("id") ON DELETE SET NULL,
    "status_id" INT REFERENCES "amocrm_statuses" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_additional__phone_c31c05" ON "additional_services_ticket" ("phone");
COMMENT ON COLUMN "additional_services_ticket"."id" IS 'ID';
COMMENT ON COLUMN "additional_services_ticket"."cost" IS 'Стоимость';
COMMENT ON COLUMN "additional_services_ticket"."full_name" IS 'ФИО клиента';
COMMENT ON COLUMN "additional_services_ticket"."phone" IS 'Номер телефона';
COMMENT ON TABLE "additional_services_ticket" IS 'Заявка на доп услуги';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "additional_services_condition_step";
        DROP TABLE IF EXISTS "additional_services_ticket";
        DROP TABLE IF EXISTS "additional_services_service";
        DROP TABLE IF EXISTS "additional_services_condition";
        DROP TABLE IF EXISTS "additional_services_category";
        """
