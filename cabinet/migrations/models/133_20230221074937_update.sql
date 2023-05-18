-- upgrade --
CREATE TABLE IF NOT EXISTS "users_real_ip" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "real_ip" VARCHAR(20) NOT NULL,
    "blocked" BOOL NOT NULL  DEFAULT False,
    "times" INT NOT NULL  DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "users_real_ip"."real_ip" IS 'IP адрес клиента';
COMMENT ON COLUMN "users_real_ip"."blocked" IS 'Заблокирован';
COMMENT ON COLUMN "users_real_ip"."times" IS 'Количество запросов';
COMMENT ON COLUMN "users_real_ip"."created_at" IS 'Время создания';
COMMENT ON COLUMN "users_real_ip"."updated_at" IS 'Время обновления';
COMMENT ON TABLE "users_real_ip" IS 'IP адреса клиентов';
-- downgrade --
DROP TABLE IF EXISTS "users_real_ip";
