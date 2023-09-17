from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users_amocrm_checks_history_log" (
            "id" BIGSERIAL NOT NULL PRIMARY KEY,
            "route" VARCHAR(50) NOT NULL,
            "status" INT NOT NULL,
            "query" VARCHAR(100) NOT NULL,
            "data" TEXT,
            "check_history_id" BIGINT REFERENCES "users_checks_history" ("id") ON DELETE SET NULL
        );
        COMMENT ON COLUMN "users_amocrm_checks_history_log"."id" IS 'ID';
        COMMENT ON COLUMN "users_amocrm_checks_history_log"."route" IS 'Статус ответа';
        COMMENT ON COLUMN "users_amocrm_checks_history_log"."status" IS 'Статус ответа';
        COMMENT ON COLUMN "users_amocrm_checks_history_log"."query" IS 'Квери запроса';
        COMMENT ON COLUMN "users_amocrm_checks_history_log"."data" IS 'Тело ответа(Пустое если статус ответа 200)';
        COMMENT ON COLUMN "users_amocrm_checks_history_log"."check_history_id" IS 'Проверка уникальности';
        COMMENT ON TABLE "users_amocrm_checks_history_log" IS 'Лог запросов истории проверки в AmoCrm';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "users_amocrm_checks_history_log";
    """
