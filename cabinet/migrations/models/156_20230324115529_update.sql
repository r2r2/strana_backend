-- upgrade --
ALTER TABLE "agencies_additional_agreement" ALTER COLUMN "number" DROP NOT NULL;
-- downgrade --
ALTER TABLE "agencies_additional_agreement" ALTER COLUMN "number" DROP NOT NULL;
