-- upgrade --
ALTER TABLE "questionnaire_users_answers" ADD "booking_id" INT;
ALTER TABLE "questionnaire_users_answers" ADD CONSTRAINT "fk_question_booking__e00310a8" FOREIGN KEY ("booking_id") REFERENCES "booking_booking" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "questionnaire_users_answers" DROP CONSTRAINT "fk_question_booking__e00310a8";
ALTER TABLE "questionnaire_users_answers" DROP COLUMN "booking_id";
