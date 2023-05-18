-- upgrade --
CREATE TABLE IF NOT EXISTS "questionnaire_documents_blocks" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(150),
    "sort" INT NOT NULL  DEFAULT 0,
    "matrix_id" INT REFERENCES "questionnaire_matrix" ("id") ON DELETE CASCADE,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "questionnaire_documents_blocks"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "questionnaire_documents_blocks"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "questionnaire_documents_blocks"."id" IS 'ID';
COMMENT ON COLUMN "questionnaire_documents_blocks"."title" IS 'Название';
COMMENT ON COLUMN "questionnaire_documents_blocks"."sort" IS 'Приоритет';
COMMENT ON COLUMN "questionnaire_documents_blocks"."matrix_id" IS 'Матрица';
COMMENT ON TABLE "questionnaire_documents_blocks" IS 'Блок документов опросника';;
CREATE TABLE IF NOT EXISTS "questionnaire_documents" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(150),
    "sort" INT NOT NULL  DEFAULT 0,
    "doc_blocks_id" INT REFERENCES "questionnaire_documents_blocks" ("id") ON DELETE CASCADE,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "questionnaire_documents"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "questionnaire_documents"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "questionnaire_documents"."id" IS 'ID';
COMMENT ON COLUMN "questionnaire_documents"."title" IS 'Название';
COMMENT ON COLUMN "questionnaire_documents"."sort" IS 'Приоритет';
COMMENT ON COLUMN "questionnaire_documents"."doc_blocks_id" IS 'Блоки документов';
COMMENT ON TABLE "questionnaire_documents" IS 'Документ сделки';;
CREATE TABLE IF NOT EXISTS "questionnaire_upload_documents" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "file_name" VARCHAR(150),
    "booking_id" INT REFERENCES "booking_booking" ("id") ON DELETE SET NULL,
    "uploaded_document_id" INT REFERENCES "questionnaire_documents" ("id") ON DELETE SET NULL,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "questionnaire_upload_documents"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "questionnaire_upload_documents"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "questionnaire_upload_documents"."id" IS 'ID';
COMMENT ON COLUMN "questionnaire_upload_documents"."file_name" IS 'Название файла';
COMMENT ON COLUMN "questionnaire_upload_documents"."booking_id" IS 'Сделка';
COMMENT ON COLUMN "questionnaire_upload_documents"."uploaded_document_id" IS 'Документы';
COMMENT ON TABLE "questionnaire_upload_documents" IS 'Загруженный документ опросника';
-- downgrade --
DROP TABLE IF EXISTS "questionnaire_upload_documents";
DROP TABLE IF EXISTS "questionnaire_documents";
DROP TABLE IF EXISTS "questionnaire_documents_blocks";
