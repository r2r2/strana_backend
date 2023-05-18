-- upgrade --
CREATE TABLE IF NOT EXISTS "users_checks_history" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "status" VARCHAR(20),
    "client_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL,
    "agent_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL,
    "agency_id" INT REFERENCES "agencies_agency" ("id") ON DELETE SET NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_users_check_status_74a950" ON "users_checks_history" ("status");
COMMENT ON COLUMN "users_checks_history"."id" IS 'ID';
COMMENT ON COLUMN "users_checks_history"."status" IS 'Статус проверки';
COMMENT ON COLUMN "users_checks_history"."created_at" IS 'Время проверки';
COMMENT ON COLUMN "users_checks_history"."agency_id" IS 'Агентство';
COMMENT ON COLUMN "users_checks_history"."agent_id" IS 'Агент';
COMMENT ON COLUMN "users_checks_history"."client_id" IS 'Клиент';
COMMENT ON TABLE "users_checks_history" IS 'История проверки';
-- downgrade --
DROP TABLE IF EXISTS "users_checks_history";
