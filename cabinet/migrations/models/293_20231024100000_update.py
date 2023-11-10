from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS notifications_qrcode_sms (
            id SERIAL PRIMARY KEY,
            sms_template_id INT REFERENCES notifications_sms_notification(id) ON DELETE CASCADE,
            sms_event_type VARCHAR(100),
            time_to_send TIMESTAMPTZ
        );
        
        CREATE TABLE IF NOT EXISTS notifications_qrcode_sms_city_through (
            id SERIAL PRIMARY KEY,
            qrcode_sms_id INT REFERENCES notifications_qrcode_sms(id) ON DELETE CASCADE,
            city_id INT REFERENCES cities_city(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS "notifications_qrcode_sms_eventlist_through" (
            "id" SERIAL PRIMARY KEY,
            "qrcode_sms_id" INT NOT NULL REFERENCES "notifications_qrcode_sms" ("id") ON DELETE CASCADE,
            "event_id" INT NOT NULL REFERENCES "event_list" ("id") ON DELETE SET NULL
        );
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "notifications_qrcode_sms_eventlist_through";
        DROP TABLE IF EXISTS "notifications_qrcode_sms_city_through";
        DROP TABLE IF EXISTS "notifications_qrcode_sms";
       """
