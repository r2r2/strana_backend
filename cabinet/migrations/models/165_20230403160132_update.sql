-- upgrade --
CREATE TABLE IF NOT EXISTS "users_test_user_phones" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "phone" VARCHAR(20) NOT NULL,
    "code" VARCHAR(4) NOT NULL  DEFAULT '9999'
);
CREATE INDEX IF NOT EXISTS "idx_users_test__phone_a49e5a" ON "users_test_user_phones" ("phone");
COMMENT ON COLUMN "users_test_user_phones"."id" IS 'ID';
COMMENT ON COLUMN "users_test_user_phones"."phone" IS 'Номер телефона';
COMMENT ON COLUMN "users_test_user_phones"."code" IS 'Код';
COMMENT ON TABLE "users_test_user_phones" IS 'Тестовые телефоны пользователей (аутентификация без запроса в СМС центр)';
-- downgrade --
DROP TABLE IF EXISTS "users_test_user_phones";
