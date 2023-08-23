-- upgrade --
ALTER TABLE "meetings_status_meeting" ADD "is_final" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "meetings_status_meeting" DROP COLUMN "is_final";