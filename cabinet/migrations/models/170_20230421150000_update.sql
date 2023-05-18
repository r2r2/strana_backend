-- upgrade --
ALTER TABLE public.users_user ADD COLUMN IF NOT EXISTS auth_first_at TIMESTAMPTZ NULL;
-- downgrade --
ALTER TABLE public.users_user DROP COLUMN IF EXISTS auth_first_at;
