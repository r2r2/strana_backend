-- upgrade --
CREATE TABLE IF NOT EXISTS "users_roles" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(150)
);
COMMENT ON COLUMN "users_roles"."id" IS 'ID';
COMMENT ON COLUMN "users_roles"."name" IS 'Название роли';
COMMENT ON TABLE "users_roles" IS 'Роль пользователя';
INSERT INTO "users_roles" ("name")
VALUES ('Админ'),
       ('Агент'),
       ('Клиент'),
       ('Представитель'),
       ('Менеджер');
ALTER TABLE "projects_project" ALTER COLUMN "status" SET DEFAULT 'current';
ALTER TABLE "projects_project" ALTER COLUMN "status" TYPE VARCHAR(20) USING "status"::VARCHAR(20);
CREATE TABLE IF NOT EXISTS "amocrm_actions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(150),
    "role_id" INT REFERENCES "users_roles" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "amocrm_actions"."id" IS 'ID';
COMMENT ON COLUMN "amocrm_actions"."name" IS 'Название';
COMMENT ON COLUMN "amocrm_actions"."role_id" IS 'Роль';
COMMENT ON TABLE "amocrm_actions" IS 'Модель действий в сделках';;
CREATE TABLE "amocrm_actions_statuses" ("status_id" INT NOT NULL REFERENCES "amocrm_statuses" ("id") ON DELETE CASCADE,"action_id" INT NOT NULL REFERENCES "amocrm_actions" ("id") ON DELETE CASCADE);
-- downgrade --
DROP TABLE IF EXISTS "amocrm_actions_statuses";
ALTER TABLE "projects_project" ALTER COLUMN "status" TYPE VARCHAR(11) USING "status"::VARCHAR(11);
ALTER TABLE "projects_project" ALTER COLUMN "status" SET DEFAULT 'Текущий';
DROP TABLE IF EXISTS "users_roles";
DROP TABLE IF EXISTS "amocrm_actions";
