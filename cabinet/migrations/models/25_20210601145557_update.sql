-- upgrade --
ALTER TABLE "users_user" ADD "agency_id" INT;
ALTER TABLE "users_user" ADD "is_decremented" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "users_user" ADD "duty_type" VARCHAR(20);
ALTER TABLE "users_user" ADD "is_approved" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "users_user" ADD "one_time_password" VARCHAR(200);
ALTER TABLE "users_user" ADD "discard_token" VARCHAR(100);
ALTER TABLE "users_user" ADD "work_end" DATE;
ALTER TABLE "users_user" ADD "commission" DECIMAL(5,2);
ALTER TABLE "users_user" ADD "reset_time" TIMESTAMPTZ;
ALTER TABLE "users_user" ADD "state" VARCHAR(20);
ALTER TABLE "users_user" ADD "maintained_id" INT  UNIQUE;
ALTER TABLE "users_user" ADD "status" VARCHAR(20);
ALTER TABLE "users_user" ADD "agent_id" INT;
ALTER TABLE "users_user" ADD "work_start" DATE;
ALTER TABLE "users_user" ALTER COLUMN "is_superuser" TYPE BOOL USING "is_superuser"::BOOL;
CREATE TABLE IF NOT EXISTS "agencies_agency" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "inn" VARCHAR(30) NOT NULL,
    "city" VARCHAR(30) NOT NULL,
    "is_approved" BOOL NOT NULL  DEFAULT False,
    "type" VARCHAR(20) NOT NULL,
    "files" JSONB
);
COMMENT ON COLUMN "users_user"."agency_id" IS 'Агенство';
COMMENT ON COLUMN "users_user"."is_decremented" IS 'Ставка снижена';
COMMENT ON COLUMN "users_user"."duty_type" IS 'Тип должности';
COMMENT ON COLUMN "users_user"."is_approved" IS 'Одобрен';
COMMENT ON COLUMN "users_user"."one_time_password" IS 'Единоразовый пароль';
COMMENT ON COLUMN "users_user"."discard_token" IS 'Токен сброса';
COMMENT ON COLUMN "users_user"."work_end" IS 'Окончание работ';
COMMENT ON COLUMN "users_user"."commission" IS 'Коммиссия';
COMMENT ON COLUMN "users_user"."reset_time" IS 'Время валидности ресета';
COMMENT ON COLUMN "users_user"."state" IS 'Состояние';
COMMENT ON COLUMN "users_user"."maintained_id" IS 'Главный агенства';
COMMENT ON COLUMN "users_user"."status" IS 'Статус';
COMMENT ON COLUMN "users_user"."agent_id" IS 'Агент';
COMMENT ON COLUMN "users_user"."work_start" IS 'Начало работ';
COMMENT ON COLUMN "agencies_agency"."id" IS 'ID';
COMMENT ON COLUMN "agencies_agency"."inn" IS 'ИНН';
COMMENT ON COLUMN "agencies_agency"."city" IS 'Город';
COMMENT ON COLUMN "agencies_agency"."is_approved" IS 'Подтверждено';
COMMENT ON COLUMN "agencies_agency"."type" IS 'Тип';
COMMENT ON COLUMN "agencies_agency"."files" IS 'Файлы';
COMMENT ON TABLE "agencies_agency" IS 'Агенство';;
ALTER TABLE "users_user" ADD CONSTRAINT "fk_users_us_agencies_af52e506" FOREIGN KEY ("agency_id") REFERENCES "agencies_agency" ("id") ON DELETE SET NULL;
ALTER TABLE "users_user" ADD CONSTRAINT "fk_users_us_users_us_b57bcc5c" FOREIGN KEY ("agent_id") REFERENCES "users_user" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "users_user" DROP CONSTRAINT "fk_users_us_users_us_b57bcc5c";
ALTER TABLE "users_user" DROP CONSTRAINT "fk_users_us_agencies_af52e506";
ALTER TABLE "users_user" DROP COLUMN "agency_id";
ALTER TABLE "users_user" DROP COLUMN "is_decremented";
ALTER TABLE "users_user" DROP COLUMN "duty_type";
ALTER TABLE "users_user" DROP COLUMN "is_approved";
ALTER TABLE "users_user" DROP COLUMN "one_time_password";
ALTER TABLE "users_user" DROP COLUMN "discard_token";
ALTER TABLE "users_user" DROP COLUMN "work_end";
ALTER TABLE "users_user" DROP COLUMN "commission";
ALTER TABLE "users_user" DROP COLUMN "reset_time";
ALTER TABLE "users_user" DROP COLUMN "state";
ALTER TABLE "users_user" DROP COLUMN "maintained_id";
ALTER TABLE "users_user" DROP COLUMN "status";
ALTER TABLE "users_user" DROP COLUMN "agent_id";
ALTER TABLE "users_user" DROP COLUMN "work_start";
ALTER TABLE "users_user" ALTER COLUMN "is_superuser" TYPE BOOL USING "is_superuser"::BOOL;
DROP TABLE IF EXISTS "agencies_agency";
