-- upgrade --
CREATE TABLE IF NOT EXISTS "questionnaire_func_blocks" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(150),
    "slug" VARCHAR(20) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "questionnaire_func_blocks"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "questionnaire_func_blocks"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "questionnaire_func_blocks"."id" IS 'ID';
COMMENT ON COLUMN "questionnaire_func_blocks"."title" IS 'Название';
COMMENT ON COLUMN "questionnaire_func_blocks"."slug" IS 'Slug';
COMMENT ON TABLE "questionnaire_func_blocks" IS 'Функциональный блок';;
CREATE TABLE IF NOT EXISTS "questionnaire_question_groups" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(150),
    "func_block_id" INT REFERENCES "questionnaire_func_blocks" ("id") ON DELETE CASCADE,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "questionnaire_question_groups"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "questionnaire_question_groups"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "questionnaire_question_groups"."id" IS 'ID';
COMMENT ON COLUMN "questionnaire_question_groups"."title" IS 'Название';
COMMENT ON COLUMN "questionnaire_question_groups"."func_block_id" IS 'Функциональный блок';
COMMENT ON TABLE "questionnaire_question_groups" IS 'Группа вопросов';
CREATE TABLE IF NOT EXISTS "questionnaire_questions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(150),
    "description" TEXT,
    "sort" INT NOT NULL  DEFAULT 0,
    "question_group_id" INT REFERENCES "questionnaire_question_groups" ("id") ON DELETE CASCADE,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "questionnaire_questions"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "questionnaire_questions"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "questionnaire_questions"."id" IS 'ID';
COMMENT ON COLUMN "questionnaire_questions"."title" IS 'Название';
COMMENT ON COLUMN "questionnaire_questions"."description" IS 'Тело вопроса';
COMMENT ON COLUMN "questionnaire_questions"."sort" IS 'Приоритет';
COMMENT ON COLUMN "questionnaire_questions"."question_group_id" IS 'Группа вопроса';
COMMENT ON TABLE "questionnaire_questions" IS 'Вопрос';;
CREATE TABLE IF NOT EXISTS "questionnaire_answers" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text" TEXT,
    "sort" INT NOT NULL  DEFAULT 0,
    "questions_id" INT REFERENCES "questionnaire_questions" ("id") ON DELETE CASCADE,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "questionnaire_answers"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "questionnaire_answers"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "questionnaire_answers"."id" IS 'ID';
COMMENT ON COLUMN "questionnaire_answers"."text" IS 'Тело вопроса';
COMMENT ON COLUMN "questionnaire_answers"."sort" IS 'Приоритет';
COMMENT ON COLUMN "questionnaire_answers"."questions_id" IS 'Вопросы';
COMMENT ON TABLE "questionnaire_answers" IS 'Ответ';;
-- downgrade --
DROP TABLE IF EXISTS "questionnaire_answers";
DROP TABLE IF EXISTS "questionnaire_questions";
DROP TABLE IF EXISTS "questionnaire_question_groups";
DROP TABLE IF EXISTS "questionnaire_func_blocks";
