-- upgrade --
ALTER TABLE "questionnaire_documents_blocks" ADD "required" BOOL NOT NULL  DEFAULT True;
-- downgrade --
ALTER TABLE "questionnaire_documents_blocks" DROP COLUMN "required";
