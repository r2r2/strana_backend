-- upgrade --
ALTER TABLE "users_managers" ADD "email" VARCHAR(100) NOT NULL DEFAULT 'example@yandex.ru';
-- downgrade --
ALTER TABLE "users_managers" DROP COLUMN "email";
