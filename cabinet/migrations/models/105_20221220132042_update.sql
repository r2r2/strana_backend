-- upgrade --
CREATE TABLE IF NOT EXISTS "cautions_caution" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "is_active" BOOL NOT NULL  DEFAULT False,
    "type" VARCHAR(20)   DEFAULT 'information',
    "roles" JSONB,
    "text" TEXT NOT NULL,
    "priority" INT NOT NULL,
    "expires_at" DATE,
    "created_at" DATE,
    "updated_at" DATE,
    "created_by_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL,
    "update_by_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS "users_caution_mute" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "caution_id" INT REFERENCES "cautions_caution" ("id") ON DELETE SET NULL,
    "user_id" INT REFERENCES "users_user" ("id") ON DELETE SET NULL,
    CONSTRAINT "uid_users_cauti_user_id_20e7b8" UNIQUE ("user_id", "caution_id")
);
COMMENT ON COLUMN "users_caution_mute"."caution_id" IS 'Предупреждение';
COMMENT ON COLUMN "users_caution_mute"."user_id" IS 'Пользователь';
COMMENT ON TABLE "users_caution_mute" IS 'Таблица связи тех, кого уже уведомили предупреждением';
COMMENT ON COLUMN "cautions_caution"."id" IS 'ID';
COMMENT ON COLUMN "cautions_caution"."is_active" IS 'Активное';
COMMENT ON COLUMN "cautions_caution"."type" IS 'Тип';
COMMENT ON COLUMN "cautions_caution"."roles" IS 'Доступно ролям';
COMMENT ON COLUMN "cautions_caution"."text" IS 'Выводимый текст';
COMMENT ON COLUMN "cautions_caution"."priority" IS 'Приоритет вывода';
COMMENT ON COLUMN "cautions_caution"."expires_at" IS 'Активен до';
COMMENT ON COLUMN "cautions_caution"."created_at" IS 'Когда создано';
COMMENT ON COLUMN "cautions_caution"."updated_at" IS 'Когда обновлено';
COMMENT ON COLUMN "cautions_caution"."created_by_id" IS 'Кем создано';
COMMENT ON COLUMN "cautions_caution"."update_by_id" IS 'Кем обновлено';
COMMENT ON TABLE "cautions_caution" IS 'Предупреждение, выводимые пользователям';;
-- downgrade --
DROP TABLE IF EXISTS "cautions_caution";
DROP TABLE IF EXISTS "users_caution_mute";
