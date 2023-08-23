-- upgrade --
ALTER TABLE "projects_project" DROP COLUMN "flats_reserv_time";
ALTER TABLE "buildings_building" DROP COLUMN "flats_reserv_time";
CREATE TABLE IF NOT EXISTS "booking_reservation_matrix" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_source" VARCHAR(100),
    "reservation_time" DOUBLE PRECISION
);
CREATE TABLE IF NOT EXISTS "booking_reservation_matrix_projects" (
        "id" SERIAL NOT NULL PRIMARY KEY,
        "reservation_matrix_id" INT,
        "project_id" INT,
        FOREIGN KEY ("reservation_matrix_id") REFERENCES "booking_reservation_matrix" ("id") ON DELETE CASCADE,
        FOREIGN KEY ("project_id") REFERENCES "projects_project" ("id") ON DELETE CASCADE
);

COMMENT ON COLUMN "booking_reservation_matrix"."id" IS 'ID';
COMMENT ON COLUMN "booking_reservation_matrix"."created_source" IS 'Источник создания онлайн-бронирования';
COMMENT ON COLUMN "booking_reservation_matrix"."reservation_time" IS 'Время резервирования квартир (ч)';
COMMENT ON TABLE "booking_reservation_matrix" IS 'Матрица сроков резервирования';;
-- downgrade --
ALTER TABLE "projects_project" ADD "flats_reserv_time" DOUBLE PRECISION;
ALTER TABLE "buildings_building" ADD "flats_reserv_time" DOUBLE PRECISION;
DROP TABLE IF EXISTS "booking_reservation_matrix_projects";
DROP TABLE IF EXISTS "booking_reservation_matrix";
