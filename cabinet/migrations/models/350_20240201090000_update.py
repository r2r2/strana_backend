from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
ALTER TABLE "booking_booking" DROP CONSTRAINT fk_booking__floors_f_483f1d80,
    ADD CONSTRAINT "fk_booking__floors_f_483f1d80" FOREIGN KEY ("floor_id") REFERENCES "floors_floor" ("id") ON
DELETE SET NULL;

ALTER TABLE "booking_booking" DROP CONSTRAINT fk_booking__floors_f_483f1d80,
    ADD CONSTRAINT "fk_booking__floors_f_483f1d80" FOREIGN KEY ("floor_id") REFERENCES "floors_floor" ("id") ON
DELETE SET NULL;

ALTER TABLE "booking_booking" DROP CONSTRAINT "fk_booking__amocrm_s_e79b52b5",
ADD CONSTRAINT "fk_booking__amocrm_s_e79b52b5" FOREIGN KEY ("amocrm_status_id") REFERENCES "amocrm_statuses" ("id")
    ON DELETE SET NULL;

ALTER TABLE "booking_booking" DROP CONSTRAINT "fk_booking__users_us_9bc9f9fa",
ADD CONSTRAINT "fk_booking__users_us_9bc9f9fa" FOREIGN KEY ("agent_id") REFERENCES "users_user" ("id") ON DELETE SET
    NULL;

ALTER TABLE "booking_booking" DROP CONSTRAINT "fk_booking__agencies_31e4c56a",
ADD CONSTRAINT "fk_booking__agencies_31e4c56a" FOREIGN KEY ("agency_id") REFERENCES "agencies_agency" ("id") ON
DELETE SET NULL;

ALTER TABLE "booking_booking" DROP CONSTRAINT "booking_booking_project_id_fkey",
ADD CONSTRAINT "booking_booking_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "projects_project" ("id") ON
DELETE SET NULL;

ALTER TABLE "booking_booking" DROP CONSTRAINT "booking_booking_building_id_fkey",
ADD CONSTRAINT "booking_booking_building_id_fkey" FOREIGN KEY ("building_id") REFERENCES "buildings_building" ("id") ON
DELETE SET NULL;

ALTER TABLE "booking_booking" DROP CONSTRAINT "booking_booking_user_id_fkey",
ADD CONSTRAINT "booking_booking_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users_user" ("id") ON
DELETE SET NULL;

ALTER TABLE "booking_booking" DROP CONSTRAINT "booking_booking_property_id_fkey",
ADD CONSTRAINT "booking_booking_property_id_fkey" FOREIGN KEY ("property_id") REFERENCES "properties_property" ("id") ON
DELETE SET NULL;

ALTER TABLE "booking_booking" DROP CONSTRAINT "booking_booking_bank_contact_info_id_fkey",
ADD CONSTRAINT "booking_booking_bank_contact_info_id_fkey" FOREIGN KEY ("bank_contact_info_id") REFERENCES "booking_bank_contact_info" ("id") ON
DELETE SET NULL;

ALTER TABLE "booking_booking" DROP CONSTRAINT "booking_booking_ddu_id_fkey",
ADD CONSTRAINT "booking_booking_ddu_id_fkey" FOREIGN KEY ("ddu_id") REFERENCES "booking_ddu" ("id") ON
DELETE SET NULL;

ALTER TABLE "booking_booking" DROP CONSTRAINT "booking_booking_booking_source_id_fkey",
ADD CONSTRAINT "booking_booking_booking_source_id_fkey" FOREIGN KEY ("booking_source_id") REFERENCES "booking_source" ("id") ON
DELETE SET NULL;

ALTER TABLE "booking_bookinglog" DROP CONSTRAINT "booking_bookinglog_booking_id_fkey",
ADD CONSTRAINT "booking_bookinglog_booking_id_fkey" FOREIGN KEY ("booking_id") REFERENCES "booking_booking" ("id") ON
DELETE SET NULL;

ALTER TABLE "users_userlog" DROP CONSTRAINT "users_userlog_user_id_fkey",
ADD CONSTRAINT "users_userlog_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users_user" ("id") ON
DELETE SET NULL;

ALTER TABLE "agencies_agencylog" DROP CONSTRAINT "agencies_agencylog_agency_id_fkey",
ADD CONSTRAINT "agencies_agencylog_agency_id_fkey" FOREIGN KEY ("agency_id") REFERENCES "agencies_agency" ("id") ON
DELETE SET NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_booking" DROP CONSTRAINT fk_booking__floors_f_483f1d80,
    ADD CONSTRAINT "fk_booking__floors_f_483f1d80" FOREIGN KEY ("floor_id") REFERENCES "floors_floor" ("id") ON
DELETE CASCADE;

ALTER TABLE "booking_booking" DROP CONSTRAINT fk_booking__floors_f_483f1d80,
    ADD CONSTRAINT "fk_booking__floors_f_483f1d80" FOREIGN KEY ("floor_id") REFERENCES "floors_floor" ("id") ON
DELETE CASCADE;

ALTER TABLE "booking_booking" DROP CONSTRAINT "fk_booking__amocrm_s_e79b52b5",
ADD CONSTRAINT "fk_booking__amocrm_s_e79b52b5" FOREIGN KEY ("amocrm_status_id") REFERENCES "amocrm_statuses" ("id")
    ON DELETE CASCADE;

ALTER TABLE "booking_booking" DROP CONSTRAINT "fk_booking__users_us_9bc9f9fa",
ADD CONSTRAINT "fk_booking__users_us_9bc9f9fa" FOREIGN KEY ("agent_id") REFERENCES "users_user" ("id") ON DELETE CASCADE;

ALTER TABLE "booking_booking" DROP CONSTRAINT "fk_booking__agencies_31e4c56a",
ADD CONSTRAINT "fk_booking__agencies_31e4c56a" FOREIGN KEY ("agency_id") REFERENCES "agencies_agency" ("id") ON
DELETE CASCADE;

ALTER TABLE "booking_booking" DROP CONSTRAINT "booking_booking_project_id_fkey",
ADD CONSTRAINT "booking_booking_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "projects_project" ("id") ON
DELETE CASCADE;

ALTER TABLE "booking_booking" DROP CONSTRAINT "booking_booking_building_id_fkey",
ADD CONSTRAINT "booking_booking_building_id_fkey" FOREIGN KEY ("building_id") REFERENCES "buildings_building" ("id") ON
DELETE CASCADE;

ALTER TABLE "booking_booking" DROP CONSTRAINT "booking_booking_user_id_fkey",
ADD CONSTRAINT "booking_booking_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users_user" ("id") ON
DELETE CASCADE;

ALTER TABLE "booking_booking" DROP CONSTRAINT "booking_booking_property_id_fkey",
ADD CONSTRAINT "booking_booking_property_id_fkey" FOREIGN KEY ("property_id") REFERENCES "properties_property" ("id") ON
DELETE CASCADE;

ALTER TABLE "booking_booking" DROP CONSTRAINT "booking_booking_bank_contact_info_id_fkey",
ADD CONSTRAINT "booking_booking_bank_contact_info_id_fkey" FOREIGN KEY ("bank_contact_info_id") REFERENCES "booking_bank_contact_info" ("id") ON
DELETE CASCADE;

ALTER TABLE "booking_booking" DROP CONSTRAINT "booking_booking_ddu_id_fkey",
ADD CONSTRAINT "booking_booking_ddu_id_fkey" FOREIGN KEY ("ddu_id") REFERENCES "booking_ddu" ("id") ON
DELETE CASCADE;

ALTER TABLE "booking_booking" DROP CONSTRAINT "booking_booking_booking_source_id_fkey",
ADD CONSTRAINT "booking_booking_booking_source_id_fkey" FOREIGN KEY ("booking_source_id") REFERENCES "booking_source" ("id") ON
DELETE CASCADE;

ALTER TABLE "booking_bookinglog" DROP CONSTRAINT "booking_bookinglog_booking_id_fkey",
ADD CONSTRAINT "booking_bookinglog_booking_id_fkey" FOREIGN KEY ("booking_id") REFERENCES "booking_booking" ("id") ON
DELETE CASCADE;

ALTER TABLE "users_userlog" DROP CONSTRAINT "users_userlog_user_id_fkey",
ADD CONSTRAINT "users_userlog_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users_user" ("id") ON
DELETE CASCADE;

ALTER TABLE "agencies_agencylog" DROP CONSTRAINT "agencies_agencylog_agency_id_fkey",
ADD CONSTRAINT "agencies_agencylog_agency_id_fkey" FOREIGN KEY ("agency_id") REFERENCES "agencies_agency" ("id") ON
DELETE CASCADE;"""
