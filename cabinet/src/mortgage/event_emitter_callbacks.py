from src.booking.constants import BookingEventSlugs
from src.booking.repos import BookingEventHistoryRepo, BookingEventRepo
from src.users.repos import User

SYSTEM_USER = "system"


async def _event_handler_ticket_change_status(
        event_emitter,
        booking_id,
        user: User,
        mortgage_ticket_inform,
):
    booking_event_history_repo = BookingEventHistoryRepo()
    booking_event_repo = BookingEventRepo()

    filters = dict(slug=BookingEventSlugs.MORTGAGE_APPLICATION_STATUS_CHANGED)

    event = await booking_event_repo.retrieve(
        filters=filters,
        related_fields=["event_type"],
    )
    actor = f"{user.full_name} <{user.amocrm_id}>" if user is not None else SYSTEM_USER
    if event is None:
        event_emitter.ee.emit('error', f"Event with slug={BookingEventSlugs.MORTGAGE_APPLICATION_STATUS_CHANGED} not found.")

    event_data = dict(
        booking_id=booking_id,
        actor=actor,
        event=event,
        event_slug=event.slug,
        event_type_name=event.event_type.event_type_name,
        event_name=event.event_name,
        event_description=event.event_description,
        mortgage_ticket_inform=mortgage_ticket_inform,
    )

    event_history = await booking_event_history_repo.create(
        data=event_data
    )


async def _event_handler_ticket_create(
        event_emitter,
        booking_id,
        user: User | None,
        mortgage_ticket_inform,
):
    booking_event_history_repo = BookingEventHistoryRepo()
    booking_event_repo = BookingEventRepo()

    filters = dict(slug=BookingEventSlugs.CREATE_MORTGAGE_APPLICATION)

    event = await booking_event_repo.retrieve(
        filters=filters,
        related_fields=["event_type"],
    )
    actor = f"{user.full_name} <{user.amocrm_id}>" if user is not None else SYSTEM_USER
    if event is None:
        event_emitter.ee.emit('error', f"Event with slug={BookingEventSlugs.CREATE_MORTGAGE_APPLICATION} not found.")

    event_data = dict(
        booking_id=booking_id,
        actor=actor,
        event=event,
        event_slug=event.slug,
        event_type_name=event.event_type.event_type_name,
        event_name=event.event_name,
        event_description=event.event_description,
        mortgage_ticket_inform=mortgage_ticket_inform,
    )

    event_history = await booking_event_history_repo.create(
        data=event_data
    )
