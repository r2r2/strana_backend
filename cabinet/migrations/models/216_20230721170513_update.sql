-- upgrade --
ALTER TABLE "event_calendar_event" ADD "format_type" VARCHAR(10) NOT NULL;
ALTER TABLE "event_event_tag" RENAME COLUMN "text_color" TO "background_color";
ALTER TABLE "event_event_tag" RENAME COLUMN "name" TO "label";
CREATE TABLE IF NOT EXISTS "event_calendar_event_type_settings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "type" VARCHAR(10) NOT NULL UNIQUE,
    "color" VARCHAR(40) NOT NULL  DEFAULT '#808080'
);
COMMENT ON COLUMN "event_calendar_event_type_settings"."id" IS 'ID';
COMMENT ON COLUMN "event_calendar_event_type_settings"."type" IS 'Тип события календаря';
COMMENT ON COLUMN "event_calendar_event_type_settings"."color" IS 'Цвет типа события календаря';
COMMENT ON TABLE "event_calendar_event_type_settings" IS 'Настройки типов событий календаря.';
CREATE TABLE IF NOT EXISTS "meetings_status_meeting" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "sort" INT NOT NULL  DEFAULT 0,
    "slug" VARCHAR(20) NOT NULL UNIQUE,
    "label" VARCHAR(40) NOT NULL
);
COMMENT ON COLUMN "meetings_status_meeting"."id" IS 'ID';
COMMENT ON COLUMN "meetings_status_meeting"."sort" IS 'Сортировка';
COMMENT ON COLUMN "meetings_status_meeting"."slug" IS 'Слаг';
COMMENT ON COLUMN "meetings_status_meeting"."label" IS 'Название статуса встречи';
COMMENT ON TABLE "meetings_status_meeting" IS 'Модель статуса встречи.';
-- downgrade --
ALTER TABLE "event_event_tag" RENAME COLUMN "background_color" TO "text_color";
ALTER TABLE "event_event_tag" RENAME COLUMN "label" TO "name";
ALTER TABLE "event_calendar_event" DROP COLUMN "format_type";
DROP TABLE IF EXISTS "event_calendar_event_type_settings";
DROP TABLE IF EXISTS "meetings_status_meeting";
