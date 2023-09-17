-- upgrade --
ALTER TABLE "users_checks" ADD "button_pressed" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "users_checks" DROP COLUMN "button_pressed";
