-- upgrade --
CREATE TABLE IF NOT EXISTS "booking_fixing_conditions_matrix" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_source" VARCHAR(100),
    "status_on_create_id" INT REFERENCES "amocrm_group_statuses" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "booking_fixing_conditions_matrix"."id" IS 'ID';
COMMENT ON COLUMN "booking_fixing_conditions_matrix"."created_source" IS 'Источник создания онлайн-бронирования';
COMMENT ON COLUMN "booking_fixing_conditions_matrix"."status_on_create_id" IS 'Статус создаваемой сделки';
COMMENT ON TABLE "booking_fixing_conditions_matrix" IS 'Матрица условий закрепления';;
CREATE TABLE IF NOT EXISTS "booking_fixing_conditions_matrix_projects" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "fixing_conditions_matrix_id" INT,
    "project_id" INT,
    FOREIGN KEY ("fixing_conditions_matrix_id") REFERENCES "booking_fixing_conditions_matrix" ("id") ON DELETE
        CASCADE,
    FOREIGN KEY ("project_id") REFERENCES "projects_project" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "booking_fixing_conditions_matrix_projects"."id" IS 'ID';
COMMENT ON COLUMN "booking_fixing_conditions_matrix_projects"."fixing_conditions_matrix_id" IS 'Матрица сроков резервирования';
COMMENT ON COLUMN "booking_fixing_conditions_matrix_projects"."project_id" IS 'Проект';
COMMENT ON TABLE "booking_fixing_conditions_matrix_projects" IS 'Матрица условий закрепления';;
-- downgrade --
DROP TABLE IF EXISTS "booking_fixing_conditions_matrix_projects";
DROP TABLE IF EXISTS "booking_fixing_conditions_matrix";