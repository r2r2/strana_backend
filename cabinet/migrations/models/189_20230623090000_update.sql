-- upgrade --
alter table public.notifications_assignclient add column is_active bool default true;
-- downgrade --
alter table public.notifications_assignclient drop column is_active;