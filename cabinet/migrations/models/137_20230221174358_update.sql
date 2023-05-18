-- upgrade --
ALTER TABLE "questionnaire_answers" ADD "is_active" BOOL NOT NULL  DEFAULT True;
ALTER TABLE "questionnaire_answers" ADD "is_default" BOOL NOT NULL  DEFAULT True;
ALTER TABLE "questionnaire_questions" ADD "is_active" BOOL NOT NULL  DEFAULT True;
ALTER TABLE "questionnaire_questions" ADD "required_to_answer" BOOL NOT NULL  DEFAULT True;
ALTER TABLE "questionnaire_questions" ADD "type" VARCHAR(10);
CREATE TABLE IF NOT EXISTS "questionnaire_users_answers" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "answer_id" INT REFERENCES "questionnaire_answers" ("id") ON DELETE CASCADE,
    "question_id" INT REFERENCES "questionnaire_questions" ("id") ON DELETE SET NULL,
    "question_group_id" INT REFERENCES "questionnaire_question_groups" ("id") ON DELETE SET NULL,
    "user_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "questionnaire_answers"."is_active" IS 'Активность';
COMMENT ON COLUMN "questionnaire_answers"."is_default" IS 'Ответ по умолчанию';
COMMENT ON COLUMN "questionnaire_questions"."is_active" IS 'Активность';
COMMENT ON COLUMN "questionnaire_questions"."required_to_answer" IS 'Обязателен к ответу';
COMMENT ON COLUMN "questionnaire_questions"."type" IS 'Тип';
COMMENT ON COLUMN "questionnaire_users_answers"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "questionnaire_users_answers"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "questionnaire_users_answers"."id" IS 'ID';
COMMENT ON COLUMN "questionnaire_users_answers"."answer_id" IS 'Вопрос';
COMMENT ON COLUMN "questionnaire_users_answers"."question_id" IS 'Вопрос';
COMMENT ON COLUMN "questionnaire_users_answers"."question_group_id" IS 'Группа вопроса';
COMMENT ON COLUMN "questionnaire_users_answers"."user_id" IS 'Пользователь';
COMMENT ON TABLE "questionnaire_users_answers" IS 'Ответ пользователя';
-- downgrade --
ALTER TABLE "questionnaire_answers" DROP COLUMN "is_active";
ALTER TABLE "questionnaire_answers" DROP COLUMN "is_default";
ALTER TABLE "questionnaire_questions" DROP COLUMN "is_active";
ALTER TABLE "questionnaire_questions" DROP COLUMN "required_to_answer";
ALTER TABLE "questionnaire_questions" DROP COLUMN "type";
DROP TABLE IF EXISTS "questionnaire_users_answers";
