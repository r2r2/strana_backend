-- upgrade --
alter table booking_booking
    drop column mortgage_request_id;

alter table booking_booking add column mortgage_request_selected boolean;

DROP TABLE if exists "booking_mortgage_request";
-- downgrade --
create table booking_mortgage_request
(
    id    serial
        constraint booking_mortgage_request_pkey
            primary key,
    files jsonb
);

comment on column booking_mortgage_request.id is 'ID';
comment on column booking_mortgage_request.files is 'Файлы';

alter table booking_booking
    add column mortgage_request_id integer
        constraint booking_booking_mortgage_request_id_key
            unique
        constraint booking_booking_mortgage_request_id_fkey
            references booking_mortgage_request;

alter table booking_booking drop column mortgage_request_selected;