-- upgrade --
CREATE TABLE IF NOT EXISTS "historical_dispute_data" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "dispute_requested" TIMESTAMPTZ,
    "admin_update" TIMESTAMPTZ,
    "admin_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL,
    "admin_unique_status_id" INT REFERENCES "users_unique_statuses" ("id") ON DELETE CASCADE,
    "agent_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL,
    "client_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL,
    "client_agency_id" INT REFERENCES "agencies_agency" ("id") ON DELETE SET NULL,
    "dispute_agent_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL,
    "dispute_agent_agency_id" INT REFERENCES "agencies_agency" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "historical_dispute_data"."dispute_requested" IS 'Время оспаривания';
COMMENT ON COLUMN "historical_dispute_data"."admin_update" IS 'Время обновления админом';
COMMENT ON COLUMN "historical_dispute_data"."admin_id" IS 'Админ';
COMMENT ON COLUMN "historical_dispute_data"."admin_unique_status_id" IS 'Статус уникальности';
COMMENT ON COLUMN "historical_dispute_data"."agent_id" IS 'Агент';
COMMENT ON COLUMN "historical_dispute_data"."client_id" IS 'Клиент';
COMMENT ON COLUMN "historical_dispute_data"."client_agency_id" IS 'Агентство';
COMMENT ON COLUMN "historical_dispute_data"."dispute_agent_id" IS 'Оспаривающий агент';
COMMENT ON COLUMN "historical_dispute_data"."dispute_agent_agency_id" IS 'Агентство';
COMMENT ON TABLE "historical_dispute_data" IS 'Учет исторических данных оспаривания';
-- downgrade --
DROP TABLE IF EXISTS "historical_dispute_data";
