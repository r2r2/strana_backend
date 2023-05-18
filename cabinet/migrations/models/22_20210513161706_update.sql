-- upgrade --
ALTER TABLE "properties_property" DROP CONSTRAINT "properties_property_user_id_fkey";
ALTER TABLE "properties_property" DROP COLUMN "user_id";
ALTER TABLE "booking_booking" DROP COLUMN "phone_submitted";
ALTER TABLE "booking_booking" ALTER COLUMN "price_payed" TYPE BOOL USING "price_payed"::BOOL;
ALTER TABLE "booking_booking" ALTER COLUMN "params_checked" TYPE BOOL USING "params_checked"::BOOL;
-- downgrade --
ALTER TABLE "booking_booking" ADD "phone_submitted" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "booking_booking" ALTER COLUMN "price_payed" TYPE BOOL USING "price_payed"::BOOL;
ALTER TABLE "booking_booking" ALTER COLUMN "params_checked" TYPE BOOL USING "params_checked"::BOOL;
ALTER TABLE "properties_property" ADD "user_id" INT;
ALTER TABLE "properties_property" ADD CONSTRAINT "properties_property_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users_user" ("id") ON DELETE CASCADE;
