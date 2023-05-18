-- upgrade --
ALTER TABLE "users_user" DROP CONSTRAINT users_user_username_key;
ALTER TABLE "users_user" DROP CONSTRAINT users_user_email_key;
ALTER TABLE "users_user" DROP CONSTRAINT users_user_phone_key;

ALTER TABLE "users_user" ADD CONSTRAINT users_user_unique_together_username_type UNIQUE (username, type);
ALTER TABLE "users_user" ADD CONSTRAINT users_user_unique_together_phone_type UNIQUE (phone, type);
ALTER TABLE "users_user" ADD CONSTRAINT users_user_unique_together_email_type UNIQUE (email, type);

-- downgrade --
ALTER TABLE "users_user" ADD CONSTRAINT users_user_username_key UNIQUE (username);
ALTER TABLE "users_user" ADD CONSTRAINT users_user_email_key UNIQUE (email);
ALTER TABLE "users_user" ADD CONSTRAINT users_user_phone_key UNIQUE (phone);

ALTER TABLE "users_user" DROP CONSTRAINT users_user_unique_together_username_type;
ALTER TABLE "users_user" DROP CONSTRAINT users_user_unique_together_phone_type;
ALTER TABLE "users_user" DROP CONSTRAINT users_user_unique_together_email_type;
