-- upgrade --
CREATE TABLE IF NOT EXISTS "meetings_meeting" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "status" VARCHAR(20) NOT NULL  DEFAULT 'start',
    "record_link" VARCHAR(255),
    "meeting_link" VARCHAR(255),
    "meeting_address" VARCHAR(300),
    "topic" VARCHAR(20) NOT NULL  DEFAULT 'buy',
    "type" VARCHAR(20) NOT NULL  DEFAULT 'online',
    "property_type" VARCHAR(20) NOT NULL  DEFAULT 'flat',
    "date" TIMESTAMPTZ NOT NULL,
    "booking_id" INT REFERENCES "booking_booking" ("id") ON DELETE SET NULL,
    "city_id" INT REFERENCES "cities_city" ("id") ON DELETE SET NULL,
    "project_id" INT REFERENCES "projects_project" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "meetings_meeting"."id" IS 'ID';
COMMENT ON COLUMN "meetings_meeting"."status" IS 'Статус';
COMMENT ON COLUMN "meetings_meeting"."record_link" IS 'Ссылка на запись';
COMMENT ON COLUMN "meetings_meeting"."meeting_link" IS 'Ссылка на встречу';
COMMENT ON COLUMN "meetings_meeting"."meeting_address" IS 'Адрес встречи';
COMMENT ON COLUMN "meetings_meeting"."topic" IS 'Тема встречи';
COMMENT ON COLUMN "meetings_meeting"."type" IS 'Тип встречи';
COMMENT ON COLUMN "meetings_meeting"."property_type" IS 'Тип помещения';
COMMENT ON COLUMN "meetings_meeting"."date" IS 'Дата';
COMMENT ON COLUMN "meetings_meeting"."booking_id" IS 'Сделка';
COMMENT ON COLUMN "meetings_meeting"."city_id" IS 'Город';
COMMENT ON COLUMN "meetings_meeting"."project_id" IS 'Проект';
COMMENT ON TABLE "meetings_meeting" IS 'Встреча';
-- downgrade --
DROP TABLE IF EXISTS "meetings_meeting";
