-- upgrade --
CREATE TABLE IF NOT EXISTS "agencies_agencylog" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "state_before" JSONB,
    "state_after" JSONB,
    "content" TEXT,
    "error_data" TEXT,
    "response_data" TEXT,
    "use_case" VARCHAR(200),
    "agency_id" INT REFERENCES "agencies_agency" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "agencies_agencylog"."id" IS 'ID';
COMMENT ON COLUMN "agencies_agencylog"."created" IS 'Создано';
COMMENT ON COLUMN "agencies_agencylog"."state_before" IS 'Состояние до';
COMMENT ON COLUMN "agencies_agencylog"."state_after" IS 'Состояние после';
COMMENT ON COLUMN "agencies_agencylog"."content" IS 'Контент';
COMMENT ON COLUMN "agencies_agencylog"."error_data" IS 'Данные ошибки';
COMMENT ON COLUMN "agencies_agencylog"."response_data" IS 'Данные ответа';
COMMENT ON COLUMN "agencies_agencylog"."use_case" IS 'Сценарий';
COMMENT ON COLUMN "agencies_agencylog"."agency_id" IS 'Агентство';
COMMENT ON TABLE "agencies_agencylog" IS 'Лог агентства';
-- downgrade --
DROP TABLE IF EXISTS "agencies_agencylog";
