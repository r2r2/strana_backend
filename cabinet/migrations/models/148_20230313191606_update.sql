-- upgrade --
ALTER TABLE "questionnaire_upload_documents" ADD "url" VARCHAR(2083);
-- downgrade --
ALTER TABLE "questionnaire_upload_documents" DROP COLUMN "url";
