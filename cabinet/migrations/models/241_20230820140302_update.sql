-- upgrade --
CREATE TABLE IF NOT EXISTS "booking_tags_group_status_through" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "group_status_id" INT NOT NULL REFERENCES "amocrm_group_statuses" ("id") ON DELETE CASCADE,
    "tag_id" INT NOT NULL REFERENCES "booking_bookingtag" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "booking_tags_group_status_through"."id" IS 'ID';
COMMENT ON COLUMN "booking_tags_group_status_through"."group_status_id" IS 'Статус';
COMMENT ON COLUMN "booking_tags_group_status_through"."tag_id" IS 'Тег';;
ALTER TABLE "booking_fixation_notifications" ALTER COLUMN "type" TYPE VARCHAR(100) USING "type"::VARCHAR(100);
-- downgrade --
ALTER TABLE "booking_fixation_notifications" ALTER COLUMN "type" TYPE VARCHAR(100) USING "type"::VARCHAR(100);
DROP TABLE IF EXISTS "booking_tags_group_status_through";
