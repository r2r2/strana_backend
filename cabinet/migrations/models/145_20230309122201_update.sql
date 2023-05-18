-- upgrade --
ALTER TABLE "questionnaire_documents" ADD "required" BOOL NOT NULL  DEFAULT True;
ALTER TABLE "questionnaire_documents" RENAME COLUMN "title" TO "label";
ALTER TABLE "questionnaire_documents_blocks" ADD "description" TEXT;
ALTER TABLE "questionnaire_documents_blocks" ADD "label" TEXT;
-- downgrade --
ALTER TABLE "questionnaire_documents" RENAME COLUMN "label" TO "title";
ALTER TABLE "questionnaire_documents" DROP COLUMN "required";
ALTER TABLE "questionnaire_documents_blocks" DROP COLUMN "description";
ALTER TABLE "questionnaire_documents_blocks" DROP COLUMN "label";
