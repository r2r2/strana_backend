-- upgrade --
ALTER TABLE projects_project ADD COLUMN IF NOT EXISTS city_id INTEGER NULL;

UPDATE projects_project p
SET city_id = c.id
FROM cities_city c
WHERE p.city = c.slug;

ALTER TABLE projects_project
ADD CONSTRAINT fk_projects_project_city_id FOREIGN KEY (city_id)
REFERENCES cities_city (id)
ON DELETE SET NULL;

ALTER TABLE projects_project DROP COLUMN city;

CREATE TABLE IF NOT EXISTS "notifications_sms_notification" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "template_text" TEXT NOT NULL,
    "lk_type" VARCHAR(10),
    "sms_event" TEXT,
    "sms_event_slug" TEXT NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True
);

CREATE TABLE IF NOT EXISTS "notifications_assignclient" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text" TEXT NOT NULL,
    "city_id" INTEGER NOT NULL REFERENCES "cities_city" ("id") ON DELETE CASCADE,
    "sms_id" INTEGER NOT NULL REFERENCES "notifications_sms_notification" ("id") ON DELETE CASCADE,
    "default" BOOLEAN NOT NULL DEFAULT FALSE,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE users_user ADD COLUMN IF NOT EXISTS sms_send BOOLEAN NOT NULL DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS "users_confirm_client_assign" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "assigned_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "assign_confirmed_at" TIMESTAMPTZ,
    "unassigned_at" TIMESTAMPTZ,
    "agency_id" INT REFERENCES "agencies_agency" ("id") ON DELETE SET NULL,
    "agent_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL,
    "client_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL,
    "comment" TEXT
);
COMMENT ON COLUMN "users_confirm_client_assign"."id" IS 'ID';
COMMENT ON COLUMN "users_confirm_client_assign"."assigned_at" IS 'Дата и время закрепления';
COMMENT ON COLUMN "users_confirm_client_assign"."assign_confirmed_at" IS 'Дата и время подтверждения закрепления';
COMMENT ON COLUMN "users_confirm_client_assign"."unassigned_at" IS 'Дата и время отказа от агента';
COMMENT ON COLUMN "users_confirm_client_assign"."agency_id" IS 'Агентство';
COMMENT ON COLUMN "users_confirm_client_assign"."agent_id" IS 'Агент';
COMMENT ON COLUMN "users_confirm_client_assign"."client_id" IS 'Клиент';
COMMENT ON COLUMN "users_confirm_client_assign"."comment" IS 'Комментарий';
COMMENT ON TABLE "users_confirm_client_assign" IS 'Модель подтверждения закрепления клиента за агентом';

-- downgrade --
ALTER TABLE projects_project ADD COLUMN IF NOT EXISTS city VARCHAR(100) NULL;

UPDATE projects_project p
SET city = c.slug
FROM cities_city c
WHERE p.city_id = c.id;

ALTER TABLE projects_project DROP CONSTRAINT IF EXISTS fk_projects_project_city_id;
ALTER TABLE projects_project DROP COLUMN IF EXISTS city_id;
DROP TABLE IF EXISTS "notifications_assignclient";
ALTER TABLE users_user DROP COLUMN IF EXISTS sms_send;
DROP TABLE IF EXISTS "users_confirm_client_assign";
