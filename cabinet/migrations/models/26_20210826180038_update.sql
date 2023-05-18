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
ALTER TABLE "showtimes_showtime" ADD "project_id" INT;
ALTER TABLE "showtimes_showtime" ADD CONSTRAINT "fk_showtime_projects_396cf557" FOREIGN KEY ("project_id") REFERENCES "projects_project" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "showtimes_showtime" DROP CONSTRAINT "fk_showtime_projects_396cf557";
ALTER TABLE "showtimes_showtime" DROP COLUMN "project_id";
