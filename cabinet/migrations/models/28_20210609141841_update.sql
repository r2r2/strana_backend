-- upgrade --
DROP TABLE IF EXISTS "users_properties_interested";
CREATE TABLE IF NOT EXISTS "users_checks" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "status" VARCHAR(20),
    "state" VARCHAR(20),
    "agent_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL,
    "user_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_users_check_status_7bd160" ON "users_checks" ("status");
CREATE INDEX IF NOT EXISTS "idx_users_check_state_35b9bd" ON "users_checks" ("state");
COMMENT ON COLUMN "users_checks"."id" IS 'ID';
COMMENT ON COLUMN "users_checks"."status" IS 'Статус';
COMMENT ON COLUMN "users_checks"."state" IS 'Состояние';
COMMENT ON COLUMN "users_checks"."agent_id" IS 'Агент';
COMMENT ON COLUMN "users_checks"."user_id" IS 'Пользователь';
COMMENT ON TABLE "users_checks" IS 'Проверка';;
ALTER TABLE "users_user" ADD "interested_project_id" INT;
ALTER TABLE "users_user" ADD "interested_type" VARCHAR(20);
ALTER TABLE "users_user" DROP COLUMN "status";
ALTER TABLE "users_user" DROP COLUMN "state";
ALTER TABLE "users_user" ALTER COLUMN "is_decremented" TYPE BOOL USING "is_decremented"::BOOL;
CREATE INDEX "idx_users_user_surname_420bde" ON "users_user" ("surname");
CREATE INDEX "idx_users_user_patrony_6f671a" ON "users_user" ("patronymic");
CREATE INDEX "idx_users_user_name_0a917a" ON "users_user" ("name");
ALTER TABLE "agencies_agency" ADD "tags" JSONB;
ALTER TABLE "agencies_agency" ADD "amocrm_id" BIGINT;
ALTER TABLE "users_user" ADD CONSTRAINT "fk_users_us_projects_1feb7960" FOREIGN KEY ("interested_project_id") REFERENCES "projects_project" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "users_user" DROP CONSTRAINT "fk_users_us_projects_1feb7960";
ALTER TABLE "users_user" ADD "status" VARCHAR(20);
ALTER TABLE "users_user" ADD "state" VARCHAR(20);
ALTER TABLE "users_user" DROP COLUMN "interested_project_id";
ALTER TABLE "users_user" DROP COLUMN "interested_type";
ALTER TABLE "users_user" ALTER COLUMN "is_decremented" TYPE BOOL USING "is_decremented"::BOOL;
DROP INDEX "idx_users_user_surname_420bde";
DROP INDEX "idx_users_user_patrony_6f671a";
DROP INDEX "idx_users_user_name_0a917a";
ALTER TABLE "agencies_agency" DROP COLUMN "tags";
ALTER TABLE "agencies_agency" DROP COLUMN "amocrm_id";
DROP TABLE IF EXISTS "users_checks";
CREATE TABLE "users_properties_interested" ("user_id" INT NOT NULL REFERENCES "users_user" ("id") ON DELETE CASCADE,"property_id" INT NOT NULL REFERENCES "properties_property" ("id") ON DELETE SET NULL);
