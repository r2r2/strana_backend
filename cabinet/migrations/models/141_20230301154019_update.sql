-- upgrade --
CREATE INDEX "idx_questionnai_type_306afe" ON "questionnaire_questions" ("type");
ALTER TABLE "questionnaire_answers" ADD "title" VARCHAR(150);
ALTER TABLE "questionnaire_answers" ADD "hint" TEXT;
ALTER TABLE "questionnaire_answers" RENAME COLUMN "text" TO "description";
ALTER TABLE "questionnaire_questions" RENAME COLUMN "required_to_answer" TO "required";
ALTER TABLE "questionnaire_questions" ALTER COLUMN "type" SET DEFAULT 'single';
ALTER TABLE "questionnaire_questions" ALTER COLUMN "type" SET NOT NULL;
ALTER TABLE "questionnaire_questions" ALTER COLUMN "type" TYPE VARCHAR(10) USING "type"::VARCHAR(10);
-- downgrade --
ALTER TABLE "questionnaire_answers" RENAME COLUMN "description" TO "text";
ALTER TABLE "questionnaire_answers" DROP COLUMN "title";
ALTER TABLE "questionnaire_answers" DROP COLUMN "hint";
ALTER TABLE "questionnaire_questions" RENAME COLUMN "required" TO "required_to_answer";
ALTER TABLE "questionnaire_questions" ALTER COLUMN "type" TYPE VARCHAR(10) USING "type"::VARCHAR(10);
ALTER TABLE "questionnaire_questions" ALTER COLUMN "type" DROP NOT NULL;
ALTER TABLE "questionnaire_questions" ALTER COLUMN "type" DROP DEFAULT;
DROP INDEX "idx_questionnai_type_306afe";