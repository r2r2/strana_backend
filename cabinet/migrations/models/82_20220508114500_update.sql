-- upgrade --
create table notifications_clients
(
    id                              serial
        constraint notifications_clients_pkey
            primary key,
    title                           varchar(250)                                       not null,
    description                     varchar(1000)                                      not null,
    is_new                          boolean                  default true              not null,
    created_at_online_purchase_step varchar(32)                                        not null,
    moved_to_online_purchase_step   varchar(32)                                        not null,
    created_at                      timestamp with time zone default CURRENT_TIMESTAMP not null,
    booking_id                      integer                                            not null
        constraint notifications_clients_booking_id_fkey
            references booking_booking
            on delete cascade,
    property_id                     integer                                            not null
        constraint notifications_clients_property_id_fkey
            references properties_property
            on delete cascade,
    user_id                         integer                                            not null
        constraint notifications_clients_user_id_fkey
            references users_user
            on delete cascade
);

comment on table notifications_clients is 'Уведомление клиента';
comment on column notifications_clients.id is 'ID';
comment on column notifications_clients.is_new is 'Прочитано пользователем';
comment on column notifications_clients.created_at_online_purchase_step is 'Стадия онлайн-покупки сделки на момент создания записи';
comment on column notifications_clients.moved_to_online_purchase_step is 'Стадия онлайн-покупки, на которую перешла сделка';
comment on column notifications_clients.created_at is 'Дата и время создания';
comment on column notifications_clients.booking_id is 'Сделка';
comment on column notifications_clients.property_id is 'Собственность';
comment on column notifications_clients.user_id is 'Сделка';

create index idx_notificatio_is_new_b59167
    on notifications_clients (is_new);


-- downgrade --
DROP TABLE IF EXISTS "booking_history";
