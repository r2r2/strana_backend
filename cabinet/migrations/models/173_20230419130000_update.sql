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