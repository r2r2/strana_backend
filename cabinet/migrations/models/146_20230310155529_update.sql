-- upgrade --
DROP TABLE IF EXISTS "questionnaire_upload_documents";
CREATE TABLE IF NOT EXISTS "questionnaire_upload_documents" (
    "id" UUID NOT NULL PRIMARY KEY,
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