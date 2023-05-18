-- upgrade --
ALTER TABLE "amocrm_pipelines" ADD "is_main" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "amocrm_pipelines" ADD "sort" INT NOT NULL  DEFAULT 0;
ALTER TABLE "amocrm_pipelines" ADD "city_id" INT;
ALTER TABLE "amocrm_pipelines" ADD "account_id" INT;
ALTER TABLE "amocrm_pipelines" ADD "is_archive" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "amocrm_pipelines" ALTER COLUMN "name" TYPE VARCHAR(150) USING "name"::VARCHAR(150);
ALTER TABLE "amocrm_statuses" ADD "color" VARCHAR(40);
ALTER TABLE "amocrm_statuses" ADD "sort" INT NOT NULL  DEFAULT 0;
ALTER TABLE "amocrm_statuses" ALTER COLUMN "name" DROP NOT NULL;
ALTER TABLE "amocrm_statuses" ALTER COLUMN "name" TYPE VARCHAR(150) USING "name"::VARCHAR(150);
ALTER TABLE "amocrm_pipelines" ADD CONSTRAINT "fk_amocrm_p_cities_c_a550ab4e" FOREIGN KEY ("city_id") REFERENCES "cities_city" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "amocrm_pipelines" DROP CONSTRAINT "fk_amocrm_p_cities_c_a550ab4e";
ALTER TABLE "amocrm_statuses" DROP COLUMN "color";
ALTER TABLE "amocrm_statuses" DROP COLUMN "sort";
ALTER TABLE "amocrm_statuses" ALTER COLUMN "name" SET NOT NULL;
ALTER TABLE "amocrm_statuses" ALTER COLUMN "name" TYPE VARCHAR(150) USING "name"::VARCHAR(150);
ALTER TABLE "amocrm_pipelines" DROP COLUMN "is_main";
ALTER TABLE "amocrm_pipelines" DROP COLUMN "sort";
ALTER TABLE "amocrm_pipelines" DROP COLUMN "city_id";
ALTER TABLE "amocrm_pipelines" DROP COLUMN "account_id";
ALTER TABLE "amocrm_pipelines" DROP COLUMN "is_archive";
ALTER TABLE "amocrm_pipelines" ALTER COLUMN "name" TYPE VARCHAR(150) USING "name"::VARCHAR(150);
