-- upgrade --
CREATE TABLE IF NOT EXISTS "common_log_email_notification" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "topic" TEXT,
    "text" TEXT,
    "lk_type" VARCHAR(10),
    "mail_event_slug" VARCHAR(100),
    "recipient_emails" TEXT,
    "is_sent" BOOL NOT NULL  DEFAULT False
);
COMMENT ON COLUMN "common_log_email_notification"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "common_log_email_notification"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "common_log_email_notification"."id" IS 'ID';
COMMENT ON COLUMN "common_log_email_notification"."topic" IS 'Заголовок письма';
COMMENT ON COLUMN "common_log_email_notification"."text" IS 'Текст письма';
COMMENT ON COLUMN "common_log_email_notification"."lk_type" IS 'Сервис ЛК, в котором отправлено письмо';
COMMENT ON COLUMN "common_log_email_notification"."mail_event_slug" IS 'Слаг назначения события отправки письма';
COMMENT ON COLUMN "common_log_email_notification"."recipient_emails" IS 'Почтовые адреса получателей письма';
COMMENT ON COLUMN "common_log_email_notification"."is_sent" IS 'Письмо отправлено';
COMMENT ON TABLE "common_log_email_notification" IS 'Логи отправленных писем.';;
CREATE TABLE IF NOT EXISTS "common_log_sms_notification" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text" TEXT,
    "lk_type" VARCHAR(10),
    "sms_event_slug" VARCHAR(100),
    "recipient_phone" VARCHAR(20),
    "is_sent" BOOL NOT NULL  DEFAULT False
);
COMMENT ON COLUMN "common_log_sms_notification"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "common_log_sms_notification"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "common_log_sms_notification"."id" IS 'ID';
COMMENT ON COLUMN "common_log_sms_notification"."text" IS 'Текст смс сообщения';
COMMENT ON COLUMN "common_log_sms_notification"."lk_type" IS 'Сервис ЛК, в котором отправлено смс сообщение';
COMMENT ON COLUMN "common_log_sms_notification"."sms_event_slug" IS 'Слаг назвачения события отправки смс';
COMMENT ON COLUMN "common_log_sms_notification"."recipient_phone" IS 'Номер телефона получателя';
COMMENT ON COLUMN "common_log_sms_notification"."is_sent" IS 'Сообщение отправлено';
COMMENT ON TABLE "common_log_sms_notification" IS 'Логи отправленных cмс сообщений.';;
-- downgrade --
DROP TABLE IF EXISTS "common_log_email_notification";
DROP TABLE IF EXISTS "common_log_sms_notification";
