-- upgrade --
ALTER TABLE "buildings_building" ALTER COLUMN "default_commission" SET DEFAULT 1;
-- downgrade --
ALTER TABLE "buildings_building" ALTER COLUMN "default_commission" DROP DEFAULT;
