from src.booking.constants import BookingEventSlugs
from src.booking.repos import (
    Booking,
    BookingEventHistoryRepo,
    BookingEventRepo,
    DocumentArchiveRepo,
    BookingRepo,
)
from src.users.repos import User
from src.booking.services.cancel_loyalty_reward_service import *

SYSTEM_USER = "system"


async def _event_handler_booking_time_out_repeat(event_emitter, booking: Booking):
    booking_event_history_repo = BookingEventHistoryRepo()
    booking_event_repo = BookingEventRepo()

    filters = dict(slug=BookingEventSlugs.TIME_EXPIRED)

    event = await booking_event_repo.retrieve(
        filters=filters,
        related_fields=["event_type"],
    )

    if event is None:
        event_emitter.ee.emit('error', f"Event with slug={BookingEventSlugs.TIME_EXPIRED} not found.")

    event_data = dict(
        booking=booking,
        actor=SYSTEM_USER,
        event=event,
        event_slug=event.slug,
        event_type_name=event.event_type.event_type_name,
        event_name=event.event_name,
        event_description=event.event_description,

    )

    if not await booking_event_history_repo.exists(filters=event_data):
        event_history = await booking_event_history_repo.create(
            data=event_data
        )


async def _event_handler_booking_payed(event_emitter, booking: Booking, user: User | None, old_group_status: str):
    booking_event_history_repo = BookingEventHistoryRepo()
    booking_event_repo = BookingEventRepo()

    filters = dict(slug=BookingEventSlugs.BOOKING_SUCCESSFULLY_PAID)

    event = await booking_event_repo.retrieve(
        filters=filters,
        related_fields=["event_type"],
    )
    actor = f"{user.full_name} <{user.amocrm_id}>" if user is not None else SYSTEM_USER
    if event is None:
        event_emitter.ee.emit('error', f"Event with slug={BookingEventSlugs.BOOKING_SUCCESSFULLY_PAID} not found.")

    event_data = dict(
        booking=booking,
        actor=actor,
        event=event,
        event_slug=event.slug,
        event_type_name=event.event_type.event_type_name,
        event_name=event.event_name,
        event_description=event.event_description,
        group_status_until=old_group_status,
        group_status_after=booking.amocrm_substage,
    )

    event_history = await booking_event_history_repo.create(
        data=event_data
    )


async def _event_handler_pay_booking(event_emitter, booking: Booking, user: User | None, old_group_status: str):
    booking_event_history_repo = BookingEventHistoryRepo()
    booking_event_repo = BookingEventRepo()

    filters = dict(slug=BookingEventSlugs.PAY_BOOKING)

    event = await booking_event_repo.retrieve(
        filters=filters,
        related_fields=["event_type"],
    )
    actor = f"{user.full_name} <{user.amocrm_id}>" if user is not None else SYSTEM_USER
    if event is None:
        event_emitter.ee.emit('error', f"Event with slug={BookingEventSlugs.PAY_BOOKING} not found.")

    event_data = dict(
        booking=booking,
        actor=actor,
        event=event,
        event_slug=event.slug,
        event_type_name=event.event_type.event_type_name,
        event_name=event.event_name,
        event_description=event.event_description,
        group_status_until=old_group_status,
        group_status_after=booking.amocrm_substage,
    )

    event_history = await booking_event_history_repo.create(
        data=event_data
    )


async def _event_handler_booking_created(
        event_emitter,
        booking: Booking,
        user: User | None,
):
    booking_event_history_repo = BookingEventHistoryRepo()
    booking_event_repo = BookingEventRepo()

    filters = dict(slug=BookingEventSlugs.CREATE_DEAL)

    event = await booking_event_repo.retrieve(
        filters=filters,
        related_fields=["event_type"],
    )
    actor = f"{user.full_name} <{user.amocrm_id}>" if user is not None else SYSTEM_USER
    if event is None:
        event_emitter.ee.emit('error', f"Event with slug={BookingEventSlugs.CREATE_DEAL} not found.")

    event_data = dict(
        booking=booking,
        actor=actor,
        event=event,
        event_slug=event.slug,
        event_type_name=event.event_type.event_type_name,
        event_name=event.event_name,
        event_description=event.event_description,
        group_status_after=booking.amocrm_substage,
    )

    event_history = await booking_event_history_repo.create(
        data=event_data
    )


async def _event_handler_personal_filled(
    event_emitter,
    booking: Booking,
    user: User,
    old_group_status: str,
):
    booking_event_history_repo = BookingEventHistoryRepo()
    booking_event_repo = BookingEventRepo()

    filters = dict(slug=BookingEventSlugs.FILL_PERSONAL_INFORMATION)

    event = await booking_event_repo.retrieve(
        filters=filters,
        related_fields=["event_type"],
    )
    actor = f"{user.full_name} <{user.amocrm_id}>" if user is not None else SYSTEM_USER
    if event is None:
        event_emitter.ee.emit('error', f"Event with slug={BookingEventSlugs.FILL_PERSONAL_INFORMATION} not found.")

    event_data = dict(
        booking=booking,
        actor=actor,
        event=event,
        event_slug=event.slug,
        event_type_name=event.event_type.event_type_name,
        event_name=event.event_name,
        event_description=event.event_description,
        group_status_until=old_group_status,
        group_status_after=booking.amocrm_substage,
    )

    event_history = await booking_event_history_repo.create(
        data=event_data
    )


async def _event_handler_accept_contract(
        event_emitter,
        booking: Booking,
        user: User,
        city: str | None,
):
    booking_event_history_repo = BookingEventHistoryRepo()
    document_archive_repo = DocumentArchiveRepo()
    booking_event_repo = BookingEventRepo()

    filters = dict(slug=BookingEventSlugs.READ_CONTRACT_OFFER)

    event = await booking_event_repo.retrieve(
        filters=filters,
        related_fields=["event_type"],
    )
    actor = f"{user.full_name} <{user.amocrm_id}>" if user is not None else SYSTEM_USER
    filters = dict(slug=city)
    signed_offer = await document_archive_repo.list(filters=filters, ordering="-date_time").first()

    if event is None:
        event_emitter.ee.emit('error', f"Event with slug={BookingEventSlugs.READ_CONTRACT_OFFER} not found.")

    event_data = dict(
        booking=booking,
        actor=actor,
        event=event,
        event_slug=event.slug,
        event_type_name=event.event_type.event_type_name,
        event_name=event.event_name,
        event_description=event.event_description,
        group_status_after=booking.amocrm_substage,
        signed_offer=signed_offer,
    )

    event_history = await booking_event_history_repo.create(
        data=event_data
    )


async def _event_handler_change_status(
        event_emitter,
        booking: Booking,
        user: User | None,
        old_group_status: str,
):
    booking_event_history_repo = BookingEventHistoryRepo()
    booking_event_repo = BookingEventRepo()

    filters = dict(slug=BookingEventSlugs.CHANGE_DEAL_GROUPING_STATUS)

    event = await booking_event_repo.retrieve(
        filters=filters,
        related_fields=["event_type"],
    )
    actor = f"{user.full_name} <{user.amocrm_id}>" if user is not None else SYSTEM_USER
    if event is None:
        event_emitter.ee.emit('error', f"Event with slug={BookingEventSlugs.CHANGE_DEAL_GROUPING_STATUS} not found.")

    event_data = dict(
        booking=booking,
        actor=actor,
        event=event,
        event_slug=event.slug,
        event_type_name=event.event_type.event_type_name,
        event_name=event.event_name,
        event_description=event.event_description,
        group_status_until=old_group_status,
        group_status_after=booking.amocrm_substage,
    )

    event_history = await booking_event_history_repo.create(
        data=event_data
    )


async def _event_handler_extend_free_booking(
        event_emitter,
        booking: Booking,
        user: User | None,
        old_group_status: str,
):
    booking_event_history_repo = BookingEventHistoryRepo()
    booking_event_repo = BookingEventRepo()

    filters = dict(slug=BookingEventSlugs.EXTEND_FREE_BOOKING)

    event = await booking_event_repo.retrieve(
        filters=filters,
        related_fields=["event_type"],
    )
    actor = f"{user.full_name} <{user.amocrm_id}>" if user is not None else SYSTEM_USER
    if event is None:
        event_emitter.ee.emit('error', f"Event with slug={BookingEventSlugs.EXTEND_FREE_BOOKING} not found.")

    event_data = dict(
        booking=booking,
        actor=actor,
        event=event,
        event_slug=event.slug,
        event_type_name=event.event_type.event_type_name,
        event_name=event.event_name,
        event_description=event.event_description,
        group_status_until=old_group_status,
        group_status_after=booking.amocrm_substage,
    )

    event_history = await booking_event_history_repo.create(
        data=event_data
    )


async def _event_handler_cancel_loyalty_reward_from_booking(
    event_emitter,
    booking: Booking,
    comment: CancelRewardComment,
):
    cancel_loyalty_reward_service: CancelLoyaltyRewardService = CancelLoyaltyRewardService(
        booking_repo=BookingRepo,
        amocrm_class=AmoCRM,
        loyalty_api=LoyaltyAPI(),
    )
    try:
        await cancel_loyalty_reward_service(
            booking_id=booking.id,
            comment=comment,
        )
    except Exception as e:
        event_emitter.ee.emit(
            'error', f"Event for booking {booking.id=} has exception on CancelLoyaltyRewardCase: {e=}"
        )
