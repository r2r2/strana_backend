-- upgrade --
CREATE TABLE IF NOT EXISTS "showtimes_showtime" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "visit" TIMESTAMPTZ,
    "agent_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL,
    "user_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "showtimes_showtime"."id" IS 'ID';
COMMENT ON COLUMN "showtimes_showtime"."visit" IS 'Дата и время посещения';
COMMENT ON COLUMN "showtimes_showtime"."agent_id" IS 'Агент';
COMMENT ON COLUMN "showtimes_showtime"."user_id" IS 'Пользователь';
COMMENT ON TABLE "showtimes_showtime" IS 'Запись на показ';
-- downgrade --
DROP TABLE IF EXISTS "showtimes_showtime";
