-- upgrade --
ALTER TABLE "questionnaire_answers" RENAME COLUMN "questions_id" TO "question_id";
ALTER TABLE "questionnaire_answers" ADD CONSTRAINT "fk_question_question_2dc8ced4" FOREIGN KEY ("question_id") REFERENCES "questionnaire_questions" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "questionnaire_answers" DROP CONSTRAINT "fk_question_question_2dc8ced4";
ALTER TABLE "questionnaire_answers" RENAME COLUMN "question_id" TO "questions_id";
