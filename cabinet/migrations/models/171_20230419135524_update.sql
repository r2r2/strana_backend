-- upgrade --
CREATE TABLE IF NOT EXISTS "amocrm_group_statuses" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(150),
    "sort" INT NOT NULL  DEFAULT 0
);
COMMENT ON COLUMN "amocrm_group_statuses"."id" IS 'ID';
COMMENT ON COLUMN "amocrm_group_statuses"."name" IS 'Имя группирующего статуса';
COMMENT ON COLUMN "amocrm_group_statuses"."sort" IS 'Приоритет';
COMMENT ON TABLE "amocrm_group_statuses" IS 'Модель Группирующих статусов';;
ALTER TABLE "amocrm_statuses" ADD "group_status_id" INT;
ALTER TABLE "amocrm_statuses" ADD CONSTRAINT "fk_amocrm_s_amocrm_g_b279c244" FOREIGN KEY ("group_status_id") REFERENCES "amocrm_group_statuses" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "amocrm_statuses" DROP CONSTRAINT "fk_amocrm_s_amocrm_g_b279c244";
ALTER TABLE "amocrm_statuses" DROP COLUMN "group_status_id";
DROP TABLE IF EXISTS "amocrm_group_statuses";
