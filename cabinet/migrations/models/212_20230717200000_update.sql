-- upgrade --
CREATE TABLE IF NOT EXISTS "booking_notifications" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_source" VARCHAR(100),
    "hours_before_send" DOUBLE PRECISION,
    "sms_template_id" INT REFERENCES "notifications_sms_notification" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "booking_notifications"."id" IS 'ID';
COMMENT ON COLUMN "booking_notifications"."created_source" IS 'Источник создания онлайн-бронирования';
COMMENT ON COLUMN "booking_notifications"."hours_before_send" IS 'За сколько часов до момента окончания резервирования отправлять (ч)';
COMMENT ON COLUMN "booking_notifications"."sms_template_id" IS 'Шаблон смс уведомления';
COMMENT ON TABLE "booking_notifications" IS 'Уведомление при платном бронировании';;
CREATE TABLE IF NOT EXISTS booking_notifications_project_through (
    id SERIAL NOT NULL PRIMARY KEY,
    booking_notification_id INTEGER REFERENCES "booking_notifications"(id) ON DELETE CASCADE,
    project_id INTEGER REFERENCES "projects_project"(id) ON DELETE CASCADE
);
COMMENT ON COLUMN "booking_notifications_project_through"."booking_notification_id" IS 'Уведомление при платном бронировании';
COMMENT ON COLUMN "booking_notifications_project_through"."project_id" IS 'Проект (ЖК)';
COMMENT ON TABLE "booking_notifications_project_through" IS 'Проекты, для которых настроено уведомление при платном бронировании';;
ALTER TABLE "booking_booking" ADD COLUMN IF NOT EXISTS "send_notify" BOOLEAN DEFAULT TRUE;
-- downgrade --
DROP TABLE IF EXISTS "booking_notifications" CASCADE;
DROP TABLE IF EXISTS "booking_notifications_project_through" CASCADE;
ALTER TABLE "booking_booking" DROP COLUMN IF EXISTS "send_notify";
