-- upgrade --
ALTER TABLE "users_user" ADD "role_id" INT DEFAULT 3;
ALTER TABLE "users_user" ADD CONSTRAINT "fk_users_us_users_ro_1daf963f" FOREIGN KEY ("role_id") REFERENCES "users_roles" ("id") ON DELETE SET NULL;
UPDATE "users_user"
SET "role_id" = CASE
    WHEN "type" = 'admin' THEN 1
    WHEN "type" = 'agent' THEN 2
    WHEN "type" = 'client' THEN 3
    WHEN "type" = 'repres' THEN 4
    WHEN "type" = 'manager' THEN 5
    ELSE "role_id"
END;
-- downgrade --
ALTER TABLE "users_user" DROP CONSTRAINT "fk_users_us_users_ro_1daf963f";
ALTER TABLE "users_user" DROP COLUMN "role_id";
