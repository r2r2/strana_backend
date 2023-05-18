-- upgrade --
ALTER TABLE "amocrm_actions" ADD "slug" VARCHAR(20) NOT NULL  DEFAULT 'slug';
UPDATE amocrm_actions SET slug = 'create_act' WHERE name = 'Сформировать акт';
ALTER TABLE amocrm_actions ALTER COLUMN slug SET NOT NULL;
-- downgrade --
ALTER TABLE "amocrm_actions" DROP COLUMN "slug";
