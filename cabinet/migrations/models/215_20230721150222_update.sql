-- upgrade --
DROP TABLE IF EXISTS "event_event_tag_and_event";
CREATE TABLE IF NOT EXISTS "event_calendar_event" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(100),
    "type" VARCHAR(10) NOT NULL,
    "date_start" TIMESTAMPTZ NOT NULL,
    "date_end" TIMESTAMPTZ,
    "meeting_id" INT  UNIQUE REFERENCES "meetings_meeting" ("id") ON DELETE CASCADE,
    "event_id" INT  UNIQUE REFERENCES "event_event" ("id") ON DELETE CASCADE
);
CREATE TABLE "event_event_tag_and_calendar_event" (
    "calendar_event_id" INT NOT NULL REFERENCES "event_calendar_event" ("id") ON DELETE CASCADE,
    "tag_id" INT NOT NULL REFERENCES "event_event_tag" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "event_calendar_event"."id" IS 'ID';
COMMENT ON COLUMN "event_calendar_event"."title" IS 'Название события календаря';
COMMENT ON COLUMN "event_calendar_event"."type" IS 'Тип события календаря';
COMMENT ON COLUMN "event_calendar_event"."date_start" IS 'Дата и время начала события календаря';
COMMENT ON COLUMN "event_calendar_event"."date_end" IS 'Дата и время окончания события календаря';
COMMENT ON COLUMN "event_calendar_event"."meeting_id" IS 'Мероприятие';
COMMENT ON COLUMN "event_calendar_event"."event_id" IS 'Мероприятие';
COMMENT ON TABLE "event_calendar_event" IS 'Событие календаря.';
-- downgrade --
DROP TABLE IF EXISTS "event_event_tag_and_calendar_event";
DROP TABLE IF EXISTS "event_calendar_event";
CREATE TABLE "event_event_tag_and_event" ("event_id" INT NOT NULL REFERENCES "event_event" ("id") ON DELETE CASCADE,"tag_id" INT NOT NULL REFERENCES "event_event_tag" ("id") ON DELETE SET NULL);
