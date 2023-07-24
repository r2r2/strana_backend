-- upgrade --
ALTER TABLE "event_event" RENAME COLUMN "photo" TO "image";
ALTER TABLE "event_event" DROP COLUMN "landing_link";
ALTER TABLE "event_event_tag" ADD "text_color" VARCHAR(40) NOT NULL  DEFAULT '#808080';
-- downgrade --
ALTER TABLE "event_event" ADD "landing_link" TEXT;
ALTER TABLE "event_event" RENAME COLUMN "image" TO "photo";
ALTER TABLE "event_event_tag" DROP COLUMN "text_color";
