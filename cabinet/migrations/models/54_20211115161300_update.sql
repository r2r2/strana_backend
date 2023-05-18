-- upgrade --
CREATE TABLE IF NOT EXISTS "booking_ddu" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "account_number" VARCHAR(50) NOT NULL,
    "payees_bank" VARCHAR(50) NOT NULL,
    "bik" VARCHAR(50) NOT NULL,
    "corresponding_account" VARCHAR(50) NOT NULL,
    "bank_inn" VARCHAR(50) NOT NULL,
    "bank_kpp" VARCHAR(50) NOT NULL,
    "change_diffs" JSONB NOT NULL,
    "files" JSONB NOT NULL
);
COMMENT ON COLUMN "booking_ddu"."id" IS 'ID';
COMMENT ON COLUMN "booking_ddu"."account_number" IS 'Номер счёта';
COMMENT ON COLUMN "booking_ddu"."payees_bank" IS 'Банк получателя';
COMMENT ON COLUMN "booking_ddu"."bik" IS 'БИК';
COMMENT ON COLUMN "booking_ddu"."corresponding_account" IS 'Кор. счёт';
COMMENT ON COLUMN "booking_ddu"."bank_inn" IS 'ИНН банка';
COMMENT ON COLUMN "booking_ddu"."bank_kpp" IS 'КПП банка';
COMMENT ON COLUMN "booking_ddu"."change_diffs" IS 'Изменения ДДУ';
COMMENT ON COLUMN "booking_ddu"."files" IS 'Файлы';
COMMENT ON TABLE "booking_ddu" IS 'ДДУ';

CREATE TABLE IF NOT EXISTS "booking_ddu_participant" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "surname" VARCHAR(50) NOT NULL,
    "patronymic" VARCHAR(50) NOT NULL,
    "passport_serial" VARCHAR(4) NOT NULL,
    "passport_number" VARCHAR(6) NOT NULL,
    "passport_issued_by" VARCHAR(150) NOT NULL,
    "passport_department_code" VARCHAR(7) NOT NULL,
    "passport_issued_date" DATE NOT NULL,
    "relation_status" VARCHAR(20) NOT NULL,
    "is_not_resident_of_russia" BOOLEAN NOT NULL,
    "has_children" BOOLEAN NOT NULL,
    "files" JSONB NOT NULL,
    "ddu_id" INTEGER
);
ALTER TABLE "booking_ddu_participant" ADD CONSTRAINT "fk_ddu_participants_ddu_19a6488e" FOREIGN KEY ("ddu_id") REFERENCES "booking_ddu" ("id") ON DELETE CASCADE;
COMMENT ON COLUMN "booking_ddu_participant"."id" IS 'ID';
COMMENT ON COLUMN "booking_ddu_participant"."name" IS 'Имя';
COMMENT ON COLUMN "booking_ddu_participant"."surname" IS 'Фамилия';
COMMENT ON COLUMN "booking_ddu_participant"."patronymic" IS 'Отчество';
COMMENT ON COLUMN "booking_ddu_participant"."passport_serial" IS 'Серия паспорта';
COMMENT ON COLUMN "booking_ddu_participant"."passport_number" IS 'Номер паспорта';
COMMENT ON COLUMN "booking_ddu_participant"."passport_issued_by" IS 'Паспорт, кем выдан';
COMMENT ON COLUMN "booking_ddu_participant"."passport_department_code" IS 'Паспорт, код подразделения';
COMMENT ON COLUMN "booking_ddu_participant"."passport_issued_date" IS 'Дата выдачи паспорта';
COMMENT ON COLUMN "booking_ddu_participant"."relation_status" IS 'Кем приходится';
COMMENT ON COLUMN "booking_ddu_participant"."is_not_resident_of_russia" IS 'Не резидент России';
COMMENT ON COLUMN "booking_ddu_participant"."has_children" IS 'Есть дети';
COMMENT ON COLUMN "booking_ddu_participant"."files" IS 'Файлы';
COMMENT ON TABLE "booking_ddu_participant" IS 'Участник ДДУ';

-- downgrade --
ALTER TABLE "booking_ddu_participant" DROP CONSTRAINT "fk_ddu_participants_ddu_19a6488e";
DROP TABLE IF EXISTS "booking_ddu";
DROP TABLE IF EXISTS "booking_ddu_participant";
