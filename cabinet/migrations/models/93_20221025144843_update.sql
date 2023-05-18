-- upgrade --
ALTER TABLE "agencies_agency" ALTER COLUMN "signatory_sign_date" TYPE DATE USING "signatory_sign_date"::DATE;
-- downgrade --
ALTER TABLE "agencies_agency" ALTER COLUMN "signatory_sign_date" TYPE TIMESTAMPTZ USING "signatory_sign_date"::TIMESTAMPTZ;
