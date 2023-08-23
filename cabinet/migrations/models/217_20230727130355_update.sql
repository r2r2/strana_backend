-- upgrade --
INSERT INTO "meetings_status_meeting" (sort, slug, label)
VALUES
    (0, 'not_confirm', 'Не подтверждена'),
    (1, 'confirm', 'Подтверждена'),
    (2, 'start', 'Встреча началась'),
    (3, 'finish', 'Завершена'),
    (4, 'cancelled', 'Отменена');

ALTER TABLE "meetings_meeting" ADD "status_id" INT;
ALTER TABLE "meetings_meeting" ADD CONSTRAINT "fk_meetings_meetings_69bd379d" FOREIGN KEY ("status_id") REFERENCES "meetings_status_meeting" ("id") ON DELETE SET NULL;
CREATE UNIQUE INDEX "uid_meetings_st_slug_a30b1a" ON "meetings_status_meeting" ("slug");

UPDATE meetings_meeting
SET status_id = (
    SELECT meetings_status_meeting.id
    FROM meetings_status_meeting
    WHERE meetings_status_meeting.slug = meetings_meeting.status
);

ALTER TABLE "meetings_meeting" DROP COLUMN "status";

-- downgrade --
DROP INDEX "uid_meetings_st_slug_a30b1a";
ALTER TABLE "meetings_meeting" DROP CONSTRAINT "fk_meetings_meetings_69bd379d";
ALTER TABLE "meetings_meeting" ADD "status" VARCHAR(20)  DEFAULT 'not_confirm';

UPDATE meetings_meeting
SET status = (
    SELECT meetings_status_meeting.slug
    FROM meetings_status_meeting
    WHERE meetings_status_meeting.id = meetings_meeting.status_id
);

ALTER TABLE "meetings_meeting" DROP COLUMN "status_id";

DELETE FROM "meetings_status_meeting"
