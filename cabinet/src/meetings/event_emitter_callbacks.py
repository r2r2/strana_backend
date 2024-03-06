from src.booking.constants import BookingEventSlugs
from src.booking.repos import Booking, BookingEventHistoryRepo, BookingEventRepo
from src.meetings.repos import MeetingStatus
from src.users.repos import User

SYSTEM_USER = "system"


async def _event_handler_meeting_created(
        event_emitter,
        booking: Booking,
        new_status: MeetingStatus | None,
        user: User | None,
):
    booking_event_history_repo = BookingEventHistoryRepo()
    booking_event_repo = BookingEventRepo()

    filters = dict(slug=BookingEventSlugs.CREATE_MEETING)

    event = await booking_event_repo.retrieve(
        filters=filters,
        related_fields=["event_type"],
    )
    actor = f"{user.full_name} <{user.amocrm_id}>" if user is not None else SYSTEM_USER
    if event is None:
        event_emitter.ee.emit('error', f"Event with slug={BookingEventSlugs.CREATE_MEETING} not found.")

    event_data = dict(
        booking=booking,
        actor=actor,
        event=event,
        event_slug=event.slug,
        event_type_name=event.event_type.event_type_name,
        event_name=event.event_name,
        event_description=event.event_description,
        event_status_after=new_status.slug if new_status else None,
    )

    event_history = await booking_event_history_repo.create(
        data=event_data
    )


async def _event_handler_meeting_status_changed(
        event_emitter,
        booking: Booking,
        new_status: MeetingStatus | None,
        old_status: MeetingStatus | None,
        user: User | None,
):
    booking_event_history_repo = BookingEventHistoryRepo()
    booking_event_repo = BookingEventRepo()

    filters = dict(slug=BookingEventSlugs.MEETING_STATUS_CHANGED)

    event = await booking_event_repo.retrieve(
        filters=filters,
        related_fields=["event_type"],
    )
    actor = f"{user.full_name} <{user.amocrm_id}>" if user is not None else SYSTEM_USER
    if event is None:
        event_emitter.ee.emit('error', f"Event with slug={BookingEventSlugs.MEETING_STATUS_CHANGED} not found.")

    event_data = dict(
        booking=booking,
        actor=actor,
        event=event,
        event_slug=event.slug,
        event_type_name=event.event_type.event_type_name,
        event_name=event.event_name,
        event_description=event.event_description,
        event_status_until=old_status.slug if old_status else None,
        event_status_after=new_status.slug if new_status else None,
    )

    event_history = await booking_event_history_repo.create(
        data=event_data
    )
