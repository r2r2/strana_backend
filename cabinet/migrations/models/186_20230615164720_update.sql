-- upgrade --
CREATE TABLE IF NOT EXISTS "event_event" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT,
    "type" VARCHAR(10),
    "address" TEXT,
    "link" TEXT,
    "meeting_date_start" TIMESTAMPTZ,
    "meeting_date_end" TIMESTAMPTZ,
    "record_date_end" TIMESTAMPTZ,
    "manager_fio" TEXT NOT NULL,
    "manager_phone" VARCHAR(20) NOT NULL,
    "max_participants_number" INT NOT NULL  DEFAULT 0,
    "photo" VARCHAR(500),
    "landing_link" TEXT,
    "show_in_all_cities" BOOL NOT NULL  DEFAULT True,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "city_id" INT REFERENCES "cities_city" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_event_event_manager_c5f1ef" ON "event_event" ("manager_phone");
COMMENT ON COLUMN "event_event"."id" IS 'ID';
COMMENT ON COLUMN "event_event"."name" IS 'Название мероприятия';
COMMENT ON COLUMN "event_event"."description" IS 'Описание мероприятия';
COMMENT ON COLUMN "event_event"."type" IS 'Тип мероприятия';
COMMENT ON COLUMN "event_event"."address" IS 'Адрес мероприятия (офлайн)';
COMMENT ON COLUMN "event_event"."link" IS 'Ссылка на мероприятие (онлайн)';
COMMENT ON COLUMN "event_event"."meeting_date_start" IS 'Дата и время начала мероприятия';
COMMENT ON COLUMN "event_event"."meeting_date_end" IS 'Дата и время окончания мероприятия';
COMMENT ON COLUMN "event_event"."record_date_end" IS 'Дата и время окончания записи на мероприятие';
COMMENT ON COLUMN "event_event"."manager_fio" IS 'ФИО ответственного менеджера';
COMMENT ON COLUMN "event_event"."manager_phone" IS 'Номер телефона ответственного менеджера';
COMMENT ON COLUMN "event_event"."max_participants_number" IS 'Макс. количество участников мероприятия';
COMMENT ON COLUMN "event_event"."photo" IS 'Фото мероприятия';
COMMENT ON COLUMN "event_event"."landing_link" IS 'Ссылка на лендинг мероприятия';
COMMENT ON COLUMN "event_event"."show_in_all_cities" IS 'Показывать во всех городах';
COMMENT ON COLUMN "event_event"."is_active" IS 'Мероприятие активно';
COMMENT ON COLUMN "event_event"."city_id" IS 'Город мероприятия (офлайн)';
COMMENT ON TABLE "event_event" IS 'Мероприятие.';;
CREATE TABLE IF NOT EXISTS "event_event_participant" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "fio" TEXT NOT NULL,
    "phone" VARCHAR(20) NOT NULL,
    "status" VARCHAR(10) NOT NULL  DEFAULT 'recorded',
    "agent_id" INT NOT NULL REFERENCES "users_user" ("id") ON DELETE CASCADE,
    "event_id" INT NOT NULL REFERENCES "event_event" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_event_event_phone_e6fa18" ON "event_event_participant" ("phone");
COMMENT ON COLUMN "event_event_participant"."id" IS 'ID';
COMMENT ON COLUMN "event_event_participant"."fio" IS 'ФИО агента участника';
COMMENT ON COLUMN "event_event_participant"."phone" IS 'Номер телефона агента участника';
COMMENT ON COLUMN "event_event_participant"."status" IS 'Статус агента участника';
COMMENT ON COLUMN "event_event_participant"."agent_id" IS 'Агент участник';
COMMENT ON COLUMN "event_event_participant"."event_id" IS 'Мероприятие';
COMMENT ON TABLE "event_event_participant" IS 'Участник мероприятия.';;
CREATE TABLE IF NOT EXISTS "event_event_tag" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "color" VARCHAR(40) NOT NULL  DEFAULT '#808080',
    "name" VARCHAR(100) NOT NULL UNIQUE
);
COMMENT ON COLUMN "event_event_tag"."id" IS 'ID';
COMMENT ON COLUMN "event_event_tag"."color" IS 'Цвет тега';
COMMENT ON COLUMN "event_event_tag"."name" IS 'Название тега';
COMMENT ON TABLE "event_event_tag" IS 'Теги мероприятий.';
CREATE TABLE "event_event_tag_and_event" (
    "event_id" INT NOT NULL REFERENCES "event_event" ("id") ON DELETE CASCADE,
    "tag_id" INT NOT NULL REFERENCES "event_event_tag" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "event_event_tag_and_event";
DROP TABLE IF EXISTS "event_event_participant";
DROP TABLE IF EXISTS "event_event";
DROP TABLE IF EXISTS "event_event_tag";
