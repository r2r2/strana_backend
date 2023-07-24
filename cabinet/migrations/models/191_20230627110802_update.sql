-- upgrade --
ALTER TABLE "event_event" ADD "comment" TEXT;
-- downgrade --
ALTER TABLE "event_event" DROP COLUMN "comment";
