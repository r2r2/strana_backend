-- upgrade --
CREATE TABLE IF NOT EXISTS "booking_fixation_notifications" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "type" VARCHAR(100),
    "days_before_send" DOUBLE PRECISION,
    "mail_template_id" INT REFERENCES "notifications_email_notification" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "booking_fixation_notifications"."id" IS 'ID';
COMMENT ON COLUMN "booking_fixation_notifications"."type" IS 'Тип события';
COMMENT ON COLUMN "booking_fixation_notifications"."days_before_send" IS 'За сколько часов до события отправлять (ч)';
COMMENT ON COLUMN "booking_fixation_notifications"."mail_template_id" IS 'Шаблон письма';
COMMENT ON TABLE "booking_fixation_notifications" IS 'Уведомление при окончании фиксации';;
CREATE TABLE IF NOT EXISTS booking_fixation_notifications_project_through (
    id SERIAL NOT NULL PRIMARY KEY,
    booking_fixation_notification_id INTEGER REFERENCES "booking_fixation_notifications"(id) ON DELETE CASCADE,
    project_id INTEGER REFERENCES "projects_project"(id) ON DELETE CASCADE
);
COMMENT ON COLUMN "booking_fixation_notifications_project_through"."booking_fixation_notification_id" IS 'Уведомление при окончании фиксации';
COMMENT ON COLUMN "booking_fixation_notifications_project_through"."project_id" IS 'Проект (ЖК)';
COMMENT ON TABLE "booking_fixation_notifications_project_through" IS 'Проекты, для которых настроено уведомление при окончании фиксации';;
-- downgrade --
DROP TABLE IF EXISTS "booking_fixation_notifications" CASCADE;
DROP TABLE IF EXISTS "booking_fixation_notifications_project_through" CASCADE;
