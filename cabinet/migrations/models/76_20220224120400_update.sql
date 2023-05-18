-- upgrade --
alter table "booking_webhook_request" add column "created_at" timestamp with time zone default CURRENT_TIMESTAMP not null;
-- downgrade --
alter table "booking_webhook_request" drop column "created_at"
