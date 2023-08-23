-- upgrade --
CREATE TABLE "booking_tags_group_statuses_through" ("tag_id" INT NOT NULL REFERENCES "booking_bookingtag" ("id") ON
    DELETE CASCADE,"group_status_id" INT NOT NULL REFERENCES "amocrm_group_statuses" ("id") ON DELETE SET NULL);
-- downgrade --
DROP TABLE IF EXISTS "booking_tags_group_statuses_through";
