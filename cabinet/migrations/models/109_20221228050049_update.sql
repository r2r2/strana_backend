-- upgrade --
CREATE TABLE IF NOT EXISTS "agreement_status" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT NOT NULL
);
COMMENT ON COLUMN "agreement_status"."name" IS 'Название статуса';
COMMENT ON COLUMN "agreement_status"."description" IS 'Описание статуса';;
CREATE TABLE IF NOT EXISTS "agreement_type" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT NOT NULL,
    "priority" INT NOT NULL,
    "created_by_id" INT REFERENCES "users_user" ("id") ON DELETE CASCADE,
    "updated_by_id" INT REFERENCES "users_user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "agreement_type"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "agreement_type"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "agreement_type"."name" IS 'Название типа';
COMMENT ON COLUMN "agreement_type"."description" IS 'Описание статуса';
COMMENT ON COLUMN "agreement_type"."priority" IS 'Приоритет вывода';
COMMENT ON COLUMN "agreement_type"."created_by_id" IS 'Кем создано';
COMMENT ON COLUMN "agreement_type"."updated_by_id" IS 'Кем изменено';
CREATE TABLE IF NOT EXISTS "agencies_act" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "number" VARCHAR(50) NOT NULL,
    "signed_at" TIMESTAMPTZ NOT NULL,
    "template_name" VARCHAR(200) NOT NULL,
    "files" JSONB,
    "agency_id" INT NOT NULL REFERENCES "agencies_agency" ("id") ON DELETE CASCADE,
    "booking_id" INT NOT NULL REFERENCES "booking_booking" ("id") ON DELETE CASCADE,
    "created_by_id" INT REFERENCES "users_user" ("id") ON DELETE CASCADE,
    "status_id" INT NOT NULL REFERENCES "agreement_status" ("id") ON DELETE CASCADE,
    "updated_by_id" INT REFERENCES "users_user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "agencies_act"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "agencies_act"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "agencies_act"."number" IS 'Номер документа';
COMMENT ON COLUMN "agencies_act"."signed_at" IS 'Когда подписано';
COMMENT ON COLUMN "agencies_act"."template_name" IS 'Название шаблона';
COMMENT ON COLUMN "agencies_act"."files" IS 'Файлы';
COMMENT ON COLUMN "agencies_act"."agency_id" IS 'Агенство';
COMMENT ON COLUMN "agencies_act"."created_by_id" IS 'Кем создано';
COMMENT ON COLUMN "agencies_act"."status_id" IS 'Статус';
COMMENT ON COLUMN "agencies_act"."updated_by_id" IS 'Кем изменено';
COMMENT ON TABLE "agencies_act" IS 'Акты агенства';;
CREATE TABLE IF NOT EXISTS "agencies_agreement" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "number" VARCHAR(50) NOT NULL,
    "signed_at" TIMESTAMPTZ NOT NULL,
    "template_name" VARCHAR(200) NOT NULL,
    "files" JSONB,
    "agency_id" INT NOT NULL REFERENCES "agencies_agency" ("id") ON DELETE CASCADE,
    "agreement_type_id" INT NOT NULL REFERENCES "agreement_type" ("id") ON DELETE CASCADE,
    "booking_id" INT NOT NULL REFERENCES "booking_booking" ("id") ON DELETE CASCADE,
    "created_by_id" INT REFERENCES "users_user" ("id") ON DELETE CASCADE,
    "project_id" INT NOT NULL REFERENCES "projects_project" ("id") ON DELETE CASCADE,
    "status_id" INT NOT NULL REFERENCES "agreement_status" ("id") ON DELETE CASCADE,
    "updated_by_id" INT REFERENCES "users_user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "agencies_agreement"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "agencies_agreement"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "agencies_agreement"."number" IS 'Номер документа';
COMMENT ON COLUMN "agencies_agreement"."signed_at" IS 'Когда подписано';
COMMENT ON COLUMN "agencies_agreement"."template_name" IS 'Название шаблона';
COMMENT ON COLUMN "agencies_agreement"."files" IS 'Файлы';
COMMENT ON COLUMN "agencies_agreement"."agency_id" IS 'Агенство';
COMMENT ON COLUMN "agencies_agreement"."agreement_type_id" IS 'Тип документа';
COMMENT ON COLUMN "agencies_agreement"."booking_id" IS 'Бронь';
COMMENT ON COLUMN "agencies_agreement"."created_by_id" IS 'Кем создано';
COMMENT ON COLUMN "agencies_agreement"."project_id" IS 'Проект';
COMMENT ON COLUMN "agencies_agreement"."status_id" IS 'Статус';
COMMENT ON COLUMN "agencies_agreement"."updated_by_id" IS 'Кем изменено';
COMMENT ON TABLE "agencies_agreement" IS 'Договора агенства';;
-- downgrade --
DROP TABLE IF EXISTS "agencies_act";
DROP TABLE IF EXISTS "agencies_agreement";
DROP TABLE IF EXISTS "agreement_status";
DROP TABLE IF EXISTS "agreement_type";
