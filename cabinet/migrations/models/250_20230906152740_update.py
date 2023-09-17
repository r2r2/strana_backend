from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "amocrm_statuses" ADD "client_group_status_id" INT;
        CREATE TABLE IF NOT EXISTS "client_amocrm_group_statuses" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "name" VARCHAR(150),
            "sort" INT NOT NULL  DEFAULT 0,
            "color" VARCHAR(40),
            "is_final" BOOL NOT NULL  DEFAULT False,
            "show_reservation_date" BOOL NOT NULL  DEFAULT False,
            "show_booking_date" BOOL NOT NULL  DEFAULT False
        );
        COMMENT ON COLUMN "client_amocrm_group_statuses"."id" IS 'ID';
        COMMENT ON COLUMN "client_amocrm_group_statuses"."name" IS 'Имя группирующего статуса';
        COMMENT ON COLUMN "client_amocrm_group_statuses"."sort" IS 'Приоритет';
        COMMENT ON COLUMN "client_amocrm_group_statuses"."color" IS 'Цвет';
        COMMENT ON COLUMN "client_amocrm_group_statuses"."is_final" IS 'Завершающий статус';
        COMMENT ON COLUMN "client_amocrm_group_statuses"."show_reservation_date" IS 'Выводить дату резерва';
        COMMENT ON COLUMN "client_amocrm_group_statuses"."show_booking_date" IS 'Выводить дату брони';
        COMMENT ON TABLE "client_amocrm_group_statuses" IS 'Модель Группирующих статусов для клиентов';;
        CREATE TABLE "booking_tags_client_group_status_through" ("tag_id" INT NOT NULL REFERENCES "booking_bookingtag" ("id") ON DELETE CASCADE,"client_group_status_id" INT NOT NULL REFERENCES "client_amocrm_group_statuses" ("id") ON DELETE SET NULL);
        COMMENT ON TABLE "booking_tags_client_group_status_through" IS 'Теги сделок для клиентов';
        ALTER TABLE "amocrm_statuses" ADD CONSTRAINT "fk_amocrm_s_client_a_8ee938a6" FOREIGN KEY ("client_group_status_id") REFERENCES "client_amocrm_group_statuses" ("id") ON DELETE SET NULL;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "amocrm_statuses" DROP CONSTRAINT "fk_amocrm_s_client_a_8ee938a6";
        DROP TABLE IF EXISTS "booking_tags_client_group_status_through";
        ALTER TABLE "amocrm_statuses" DROP COLUMN "client_group_status_id";
        DROP TABLE IF EXISTS "client_amocrm_group_statuses";
    """
