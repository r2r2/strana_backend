-- Заполняет бд тестовыми данными

-- Случайная роль юзера
CREATE OR REPLACE FUNCTION random_role()
    RETURNS user_roles
    LANGUAGE sql
    VOLATILE PARALLEL SAFE AS
$func$
SELECT (ARRAY ['SCOUT'::user_roles,'BOOKMAKER'::user_roles,'SUPERVISOR'::user_roles])[trunc(random() * 3 + 1)::int];
$func$;

-- Случайный тип чата
CREATE OR REPLACE FUNCTION random_chat_type()
    RETURNS chattypes
    LANGUAGE sql
    VOLATILE PARALLEL SAFE AS
$func$
SELECT (
           ARRAY ['BOOKMAKER_WITH_SCOUT'::chattypes,'BOOKMAKER_WITH_SUPERVISOR'::chattypes,'SCOUT_WITH_SUPERVISOR'::chattypes]
           )[trunc(random() * 3 + 1)::int];
$func$;

do
$$
    declare
        i             integer;
        sports_count  integer := 5;
        matches_count integer := 1000;
        teams_count   integer := 50;
        chats_count   integer := 100;
        users_count   integer := 30;
    begin

        -- Create users
        for i in 1..users_count
            loop
                insert into users(sportlevel_id, name, role, created_at, updated_at, scout_number)
                values (i,
                        concat('User name #', i::char),
                        random_role(),
                        now(),
                        null,
                        i);
            end loop;

        -- Create sports
        for i in 1..sports_count
            loop
                insert into sports(id, name_ru, name_en, created_at)
                values (i,
                        concat('sport_ru', i::char),
                        concat('sport_en', i::char),
                        now());
            end loop;

        -- Create matches
        insert into matches(sportlevel_id, created_at, updated_at, start_at, finish_at, sport_id, team_a_id, team_b_id,
                            team_a_name_ru, team_a_name_en, team_b_name_ru,
                            team_b_name_en, state)
        values (generate_series(1, matches_count),
                now(),
                null,
                now() + (random() * (interval '90 days')) + '3 days',
                null,
                trunc(random() * sports_count + 1),
                trunc(random() * teams_count + 1),
                trunc(random() * teams_count + 1),
                'team_a_ru',
                'team_a_en',
                'team_b_ru',
                'team_b_en',
                'ACTIVE'::matchstates);

        -- Create chats
        for i in 1..chats_count
            loop
                insert into chats (created_at, match_id, type, meta, is_closed)
                values (now(), i / 4, random_chat_type(), '{}'::jsonb, false);

                insert into chat_membership(user_id,
                                            chat_id,
                                            created_at,
                                            last_received_message_id,
                                            last_read_message_id,
                                            user_role,
                                            has_read_permission,
                                            has_write_permission,
                                            is_primary_member)
                values (generate_series(1, users_count),
                        i,
                        now(),
                        0,
                        0,
                        random_role(),
                        true,
                        true,
                        true);

            end loop;

        -- Create tickets
        for i in 1..(chats_count - 1)
            loop
                insert into tickets(created_at, updated_at, status, assigned_to_user_id, created_from_chat_id, chat_id,
                                    comment,
                                    close_reason,
                                    created_by)
                values (now(),
                        null,
                        'NEW',
                        trunc(random() * users_count + 1),
                        trunc(random() * chats_count + 1),
                        trunc(random() * chats_count + 1),
                        null,
                        null,
                        trunc(random() * users_count + 1));

                -- Create ticket_status_logs
                insert into ticket_status_logs(ticket_id, new_status, updated_by, created_at)
                values (i, 'NEW', trunc(random() * users_count + 1), now());
            end loop;
    end;
$$
;
