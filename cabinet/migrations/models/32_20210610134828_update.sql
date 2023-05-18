-- upgrade --
CREATE TABLE IF NOT EXISTS "pages_broker_registration" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "new_pwd_image" VARCHAR(500),
    "login_pwd_image" VARCHAR(500),
    "forgot_pwd_image" VARCHAR(500),
    "forgot_send_image" VARCHAR(500),
    "login_email_image" VARCHAR(500),
    "enter_agency_image" VARCHAR(500),
    "confirm_send_image" VARCHAR(500),
    "enter_personal_image" VARCHAR(500),
    "enter_password_image" VARCHAR(500),
    "accept_contract_image" VARCHAR(500),
    "confirmed_email_image" VARCHAR(500)
);
COMMENT ON COLUMN "pages_broker_registration"."id" IS 'ID';
COMMENT ON COLUMN "pages_broker_registration"."new_pwd_image" IS 'Изображение новый пароль';
COMMENT ON COLUMN "pages_broker_registration"."login_pwd_image" IS 'Изображение логин пароль';
COMMENT ON COLUMN "pages_broker_registration"."forgot_pwd_image" IS 'Изображение забыл пароль';
COMMENT ON COLUMN "pages_broker_registration"."forgot_send_image" IS 'Изображение забыл пароль письмо';
COMMENT ON COLUMN "pages_broker_registration"."login_email_image" IS 'Изображение логин почта';
COMMENT ON COLUMN "pages_broker_registration"."enter_agency_image" IS 'Изображение ввод агенства';
COMMENT ON COLUMN "pages_broker_registration"."confirm_send_image" IS 'Изображение подтвеждение отправлено';
COMMENT ON COLUMN "pages_broker_registration"."enter_personal_image" IS 'Изображение ввод данных';
COMMENT ON COLUMN "pages_broker_registration"."enter_password_image" IS 'Изображение ввод пароля';
COMMENT ON COLUMN "pages_broker_registration"."accept_contract_image" IS 'Изображение принятие договора';
COMMENT ON COLUMN "pages_broker_registration"."confirmed_email_image" IS 'Изображение почта подтверждена';
COMMENT ON TABLE "pages_broker_registration" IS 'Регистрация брокера';
-- downgrade --
DROP TABLE IF EXISTS "pages_broker_registration";
