-- upgrade --
DELETE FROM public.users_user
WHERE amocrm_id IS NULL
AND NOT EXISTS (
  SELECT 1 FROM public.booking_booking WHERE user_id = public.users_user.id
);

-- downgrade --
