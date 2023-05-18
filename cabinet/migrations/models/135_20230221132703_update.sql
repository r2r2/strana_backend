-- upgrade --
CREATE TABLE IF NOT EXISTS "questionnaire_conditions" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(150),
    "answers_id" INT REFERENCES "questionnaire_answers" ("id") ON DELETE CASCADE,
    "question_groups_id" INT REFERENCES "questionnaire_question_groups" ("id") ON DELETE CASCADE,
    "questions_id" INT REFERENCES "questionnaire_questions" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "questionnaire_conditions"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "questionnaire_conditions"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "questionnaire_conditions"."id" IS 'ID';
COMMENT ON COLUMN "questionnaire_conditions"."title" IS 'Название';
COMMENT ON COLUMN "questionnaire_conditions"."answers_id" IS 'Ответ';
COMMENT ON COLUMN "questionnaire_conditions"."question_groups_id" IS 'Группы вопроса';
COMMENT ON COLUMN "questionnaire_conditions"."questions_id" IS 'Вопросы';
COMMENT ON TABLE "questionnaire_conditions" IS 'Условие для матрицы';;
CREATE TABLE IF NOT EXISTS "questionnaire_matrix" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(150)
);
COMMENT ON COLUMN "questionnaire_matrix"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "questionnaire_matrix"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "questionnaire_matrix"."id" IS 'ID';
COMMENT ON COLUMN "questionnaire_matrix"."title" IS 'Название';
COMMENT ON TABLE "questionnaire_matrix" IS 'Матрица';
CREATE TABLE "questionnaire_matrix_conditions" ("matrix_id" INT NOT NULL REFERENCES "questionnaire_matrix" ("id") ON DELETE CASCADE,"condition_id" INT NOT NULL REFERENCES "questionnaire_conditions" ("id") ON DELETE CASCADE);
-- downgrade --
DROP TABLE IF EXISTS "questionnaire_matrix_conditions";
DROP TABLE IF EXISTS "questionnaire_conditions";
DROP TABLE IF EXISTS "questionnaire_matrix";
