-- upgrade --
ALTER TABLE "users_roles" ADD "slug" VARCHAR(50);
UPDATE users_roles
SET slug = CASE
    WHEN name = 'Админ' THEN 'admin'
    WHEN name = 'Агент' THEN 'agent'
    WHEN name = 'Клиент' THEN 'client'
    WHEN name = 'Представитель' THEN 'repres'
    WHEN name = 'Менеджер' THEN 'manager'
    ELSE slug
    END;
-- downgrade --
ALTER TABLE "users_roles" DROP COLUMN "slug";
