-- upgrade --
ALTER TABLE "additional_agreement_templates" ADD "type" VARCHAR(50);
-- downgrade --
ALTER TABLE "additional_agreement_templates" DROP COLUMN "type";
