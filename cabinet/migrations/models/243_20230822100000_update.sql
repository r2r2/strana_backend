-- upgrade --
CREATE TABLE IF NOT EXISTS users_unique_statuses_buttons (
    id SERIAL PRIMARY KEY,
    text VARCHAR(255),
    slug VARCHAR(255),
    background_color VARCHAR(7) DEFAULT '#8F00FF',
    text_color VARCHAR(7) DEFAULT '#FFFFFF',
    description TEXT
);

insert into users_unique_statuses_buttons (text, slug)
values
	('Хочу оспорить', 'want_dispute');

alter table users_checks add column if not exists button_slug varchar(255);

-- downgrade --
DROP TABLE IF EXISTS users_unique_statuses_buttons;

alter table users_checks drop column if exists button_slug;
