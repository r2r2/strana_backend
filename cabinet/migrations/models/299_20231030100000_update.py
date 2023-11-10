from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "event_groups" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "group_id" INT,
            "timeslot" VARCHAR(24),
            "event_id" INT REFERENCES "event_list" ("id") ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS "idx_event_groups_group_id" ON "event_groups" ("group_id");
        
        CREATE TABLE IF NOT EXISTS "notifications_qrcode_sms_eventgroup_through" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "event_group_id" INT NOT NULL REFERENCES "event_groups" ("id") ON DELETE CASCADE,
            "qrcode_sms_id" INT NOT NULL REFERENCES "notifications_qrcode_sms" ("id") ON DELETE CASCADE
        );
        COMMENT ON COLUMN "notifications_qrcode_sms_eventgroup_through"."id" IS 'ID';
        COMMENT ON COLUMN "notifications_qrcode_sms_eventgroup_through"."event_group_id" IS 'Группа';
        COMMENT ON COLUMN "notifications_qrcode_sms_eventgroup_through"."qrcode_sms_id" IS 'Уведомление о QR-коде для смс';
        COMMENT ON TABLE "notifications_qrcode_sms_eventgroup_through" IS 'Группы, для которых настроено уведомление о QR-коде для смс.';
        
        ALTER TABLE "notifications_qrcode_sms" DROP COLUMN IF EXISTS sms_event_type;
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "event_groups";
        DROP TABLE IF EXISTS "notifications_qrcode_sms_eventgroup_through";
        ALTER TABLE "notifications_qrcode_sms" ADD COLUMN IF NOT EXISTS sms_event_type VARCHAR(255) NULL;
        """
