-- upgrade --
CREATE TABLE IF NOT EXISTS "booking_bank_contact_info" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "bank_name" VARCHAR(100) NOT NULL,
    "specialist_name" VARCHAR(100),
    "specialist_phone" VARCHAR(100),
    "specialist_email" VARCHAR(100)
);
COMMENT ON COLUMN "booking_bank_contact_info"."id" IS 'ID';
COMMENT ON COLUMN "booking_bank_contact_info"."bank_name" IS 'Название банка';
COMMENT ON COLUMN "booking_bank_contact_info"."specialist_name" IS 'Имя специалиста';
COMMENT ON COLUMN "booking_bank_contact_info"."specialist_phone" IS 'Номер телефона специалиста';
COMMENT ON COLUMN "booking_bank_contact_info"."specialist_email" IS 'Электронная почта специалиста';
COMMENT ON TABLE "booking_bank_contact_info" IS 'Данные для связи с банком';;
ALTER TABLE "booking_booking" ADD "bank_contact_info_id" INT  UNIQUE;
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "bank_contact_info_id";
DROP TABLE IF EXISTS "booking_bank_contact_info";
