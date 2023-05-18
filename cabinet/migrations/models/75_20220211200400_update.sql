-- upgrade --
alter table "booking_booking" add column "should_be_deactivated_by_timer" boolean not null default false;
-- downgrade --
alter table "booking_booking" drop column "should_be_deactivated_by_timer"
