-- upgrade --
ALTER TABLE "amocrm_group_statuses" ADD "show_reservation_date" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "amocrm_group_statuses" ADD "show_booking_date" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "amocrm_group_statuses" DROP COLUMN "show_reservation_date";
ALTER TABLE "amocrm_group_statuses" DROP COLUMN "show_booking_date";
