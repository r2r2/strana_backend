-- upgrade --
CREATE TABLE IF NOT EXISTS "additional_agreement_status" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT
);
COMMENT ON COLUMN "additional_agreement_status"."id" IS 'ID';
COMMENT ON COLUMN "additional_agreement_status"."name" IS 'Название статуса';
COMMENT ON COLUMN "additional_agreement_status"."description" IS 'Описание статуса';
CREATE TABLE IF NOT EXISTS "agencies_additional_agreement" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "number" VARCHAR(50) NOT NULL,
    "template_name" VARCHAR(200),
    "reason_comment" VARCHAR(300) NOT NULL,
    "signed_at" TIMESTAMPTZ,
    "files" JSONB,
    "agency_agreement_id" INT NOT NULL REFERENCES "agencies_agreement" ("id") ON DELETE CASCADE,
    "status_id" INT REFERENCES "additional_agreement_status" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "agencies_additional_agreement"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "agencies_additional_agreement"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "agencies_additional_agreement"."id" IS 'ID';
COMMENT ON COLUMN "agencies_additional_agreement"."name" IS 'Название доп. соглашения';
COMMENT ON COLUMN "agencies_additional_agreement"."number" IS 'Номер документа';
COMMENT ON COLUMN "agencies_additional_agreement"."template_name" IS 'Название шаблона';
COMMENT ON COLUMN "agencies_additional_agreement"."reason_comment" IS 'Комментарий (администратора)';
COMMENT ON COLUMN "agencies_additional_agreement"."signed_at" IS 'Когда подписано';
COMMENT ON COLUMN "agencies_additional_agreement"."files" IS 'Файлы';
COMMENT ON COLUMN "agencies_additional_agreement"."agency_agreement_id" IS 'Договор агентства';
COMMENT ON COLUMN "agencies_additional_agreement"."status_id" IS 'Статус';
COMMENT ON TABLE "agencies_additional_agreement" IS 'Дополнительное соглашение к договору агентства.';;
-- downgrade --
DROP TABLE IF EXISTS "agencies_additional_agreement";
DROP TABLE IF EXISTS "additional_agreement_status";
