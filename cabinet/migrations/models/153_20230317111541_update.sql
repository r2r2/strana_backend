-- upgrade --
ALTER TABLE "questionnaire_documents_blocks" ALTER COLUMN "required" SET DEFAULT False;
ALTER TABLE "questionnaire_documents_blocks" ALTER COLUMN "required" TYPE BOOL USING "required"::BOOL;
-- downgrade --
ALTER TABLE "questionnaire_documents_blocks" ALTER COLUMN "required" SET DEFAULT True;
ALTER TABLE "questionnaire_documents_blocks" ALTER COLUMN "required" TYPE BOOL USING "required"::BOOL;
