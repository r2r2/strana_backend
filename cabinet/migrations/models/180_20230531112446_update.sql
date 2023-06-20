-- upgrade --
ALTER TABLE "amocrm_group_statuses" ADD "is_final" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "amocrm_group_statuses" ADD "color" VARCHAR(40);
ALTER TABLE "amocrm_statuses" DROP COLUMN "color";

DROP TABLE IF EXISTS "amocrm_actions_statuses";
CREATE TABLE "amocrm_actions_group_statuses" (
    "group_status_id" INT NOT NULL REFERENCES "amocrm_group_statuses" ("id") ON DELETE CASCADE,
    "action_id" INT NOT NULL REFERENCES "amocrm_actions" ("id") ON DELETE CASCADE
);

-- downgrade --
ALTER TABLE "amocrm_statuses" ADD "color" VARCHAR(40);
ALTER TABLE "amocrm_group_statuses" DROP COLUMN "is_final";
ALTER TABLE "amocrm_group_statuses" DROP COLUMN "color";

DROP TABLE IF EXISTS "amocrm_actions_group_statuses";
CREATE TABLE "amocrm_actions_statuses" (
    "status_id" INT NOT NULL REFERENCES "amocrm_statuses" ("id") ON DELETE CASCADE,
    "action_id" INT NOT NULL REFERENCES "amocrm_actions" ("id") ON DELETE CASCADE
);
