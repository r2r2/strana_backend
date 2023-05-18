-- upgrade --
CREATE TABLE IF NOT EXISTS "pages_check_unique" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "check_image" VARCHAR(500),
    "result_image" VARCHAR(500)
);
COMMENT ON COLUMN "pages_check_unique"."id" IS 'ID';
COMMENT ON COLUMN "pages_check_unique"."check_image" IS 'Изображение проверка';
COMMENT ON COLUMN "pages_check_unique"."result_image" IS 'Изображение результат';
COMMENT ON TABLE "pages_check_unique" IS 'Проверка на уникальность';;
CREATE TABLE IF NOT EXISTS "pages_showtime_registration" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "result_image" VARCHAR(500)
);
COMMENT ON COLUMN "pages_showtime_registration"."id" IS 'ID';
COMMENT ON COLUMN "pages_showtime_registration"."result_image" IS 'Изображение результат';
COMMENT ON TABLE "pages_showtime_registration" IS 'Запись на показ';;
-- downgrade --
DROP TABLE IF EXISTS "pages_check_unique";
DROP TABLE IF EXISTS "pages_showtime_registration";
