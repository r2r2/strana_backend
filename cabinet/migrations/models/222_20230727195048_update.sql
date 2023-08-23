-- upgrade --
CREATE TABLE IF NOT EXISTS "booking_bookingtag" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "label" VARCHAR(100) NOT NULL,
    "style" VARCHAR(20) NOT NULL  DEFAULT 'default',
    "slug" VARCHAR(255) NOT NULL,
    "priority" INT,
    "is_active" BOOL NOT NULL  DEFAULT False
);
COMMENT ON COLUMN "booking_bookingtag"."id" IS 'ID';
COMMENT ON COLUMN "booking_bookingtag"."label" IS 'Название';
COMMENT ON COLUMN "booking_bookingtag"."style" IS 'Стиль';
COMMENT ON COLUMN "booking_bookingtag"."slug" IS 'Слаг тега';
COMMENT ON COLUMN "booking_bookingtag"."priority" IS 'Приоритет. Чем меньше приоритет - тем выше выводится тег в списке';
COMMENT ON COLUMN "booking_bookingtag"."is_active" IS 'Неактивные теги не выводятся на сайте';
COMMENT ON TABLE "booking_bookingtag" IS 'Тег сделки';;
INSERT INTO booking_bookingtag (label, slug, priority, is_active)
VALUES
    ('Резерв до {time}', 'reserved', 0, True),
    ('Забронировано до {time}', 'booked', 0, True),
    ('Резерв просрочен', 'expired', 0, True);
-- downgrade --
DROP TABLE IF EXISTS "booking_bookingtag";
