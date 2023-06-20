-- upgrade --
CREATE TABLE IF NOT EXISTS "notifications_email_notification" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "template_topic" TEXT NOT NULL,
    "template_text" TEXT NOT NULL,
    "lk_type" VARCHAR(10) NOT NULL,
    "mail_event" TEXT,
    "mail_event_slug" VARCHAR(100) NOT NULL  UNIQUE,
    "is_active" BOOL NOT NULL  DEFAULT True
);
COMMENT ON COLUMN "notifications_email_notification"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "notifications_email_notification"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "notifications_email_notification"."id" IS 'ID';
COMMENT ON COLUMN "notifications_email_notification"."template_topic" IS 'Заголовок шаблона письма';
COMMENT ON COLUMN "notifications_email_notification"."template_text" IS 'Текст шаблона письма';
COMMENT ON COLUMN "notifications_email_notification"."lk_type" IS 'Сервис ЛК, в котором применяется шаблон';
COMMENT ON COLUMN "notifications_email_notification"."mail_event" IS 'Описание назначения события отправки письма';
COMMENT ON COLUMN "notifications_email_notification"."mail_event_slug" IS 'Слаг назначения события отправки письма';
COMMENT ON COLUMN "notifications_email_notification"."is_active" IS 'Шаблон активен';
COMMENT ON TABLE "notifications_email_notification" IS 'Шаблоны писем.';;
CREATE TABLE IF NOT EXISTS "notifications_sms_notification" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "template_text" TEXT NOT NULL,
    "lk_type" VARCHAR(10) NOT NULL,
    "sms_event" TEXT,
    "sms_event_slug" VARCHAR(100) NOT NULL  UNIQUE,
    "is_active" BOOL NOT NULL  DEFAULT True
);
COMMENT ON COLUMN "notifications_sms_notification"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "notifications_sms_notification"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "notifications_sms_notification"."id" IS 'ID';
COMMENT ON COLUMN "notifications_sms_notification"."template_text" IS 'Текст шаблона смс сообщения';
COMMENT ON COLUMN "notifications_sms_notification"."lk_type" IS 'Сервис ЛК, в котором применяется шаблон';
COMMENT ON COLUMN "notifications_sms_notification"."sms_event" IS 'Описание назначения события отправки смс';
COMMENT ON COLUMN "notifications_sms_notification"."sms_event_slug" IS 'Слаг события отправки смс';
COMMENT ON COLUMN "notifications_sms_notification"."is_active" IS 'Шаблон активен';
COMMENT ON TABLE "notifications_sms_notification" IS 'Шаблоны cмс сообщений.';;
-- downgrade --
DROP TABLE IF EXISTS "notifications_email_notification";
DROP TABLE IF EXISTS "notifications_sms_notification";
