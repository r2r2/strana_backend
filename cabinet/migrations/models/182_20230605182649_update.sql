-- upgrade --
ALTER TABLE "meetings_meeting" ALTER COLUMN "status" SET DEFAULT 'not_confirm';
ALTER TABLE "meetings_meeting" ALTER COLUMN "type" SET DEFAULT 'kc';
-- downgrade --
ALTER TABLE "meetings_meeting" ALTER COLUMN "status" SET DEFAULT 'start';
ALTER TABLE "meetings_meeting" ALTER COLUMN "type" SET DEFAULT 'online';
