from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    CREATE TABLE IF NOT EXISTS "notifications_event_sms_notification" (
        "id" SERIAL NOT NULL PRIMARY KEY,
        "sms_event_type" VARCHAR(100),
        "days" DOUBLE PRECISION,
        "sms_template_id" INT REFERENCES "notifications_sms_notification" ("id") ON DELETE CASCADE
    );
    COMMENT ON COLUMN "notifications_event_sms_notification"."id" IS 'ID';
    COMMENT ON COLUMN "notifications_event_sms_notification"."sms_event_type" IS 'Тип события отправки смс';
    COMMENT ON COLUMN "notifications_event_sms_notification"."days" IS 'За сколько дней до / За сколько дней после события отправлять';
    COMMENT ON COLUMN "notifications_event_sms_notification"."sms_template_id" IS 'Шаблон смс';
    COMMENT ON TABLE "notifications_event_sms_notification" IS 'Уведомление для брокеров, участвующих в мероприятиях.';
    
    CREATE TABLE IF NOT EXISTS "notifications_event_sms_notifications_city_through" (
        "id" SERIAL NOT NULL PRIMARY KEY,
        "event_sms_notification_id" INT NOT NULL REFERENCES "notifications_event_sms_notification" ("id") ON DELETE CASCADE,
        "city_id" INT NOT NULL REFERENCES "cities_city" ("id") ON DELETE CASCADE
    );
    COMMENT ON COLUMN "notifications_event_sms_notifications_city_through"."event_sms_notification_id" IS 'Уведомление для брокеров, участвующих в мероприятиях';
    COMMENT ON COLUMN "notifications_event_sms_notifications_city_through"."city_id" IS 'Проект (ЖК)';
    COMMENT ON TABLE "notifications_event_sms_notifications_city_through" IS 'Проекты, для которых настроено уведомление для брокеров, участвующих в мероприятиях.';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "notifications_event_sms_notifications_city_through";
        DROP TABLE IF EXISTS "notifications_event_sms_notification";
        """
