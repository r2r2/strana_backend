from common.event_emitter.client import EventEmitter
from src.booking.event_emitter_callbacks import (
    _event_handler_accept_contract, _event_handler_booking_created,
    _event_handler_booking_payed, _event_handler_booking_time_out_repeat,
    _event_handler_change_status, _event_handler_pay_booking,
    _event_handler_personal_filled, _event_handler_extend_free_booking,
    _event_handler_cancel_loyalty_reward_from_booking,
)
from src.users.repos import User

event_emitter = EventEmitter()


@event_emitter.ee.on('booking_time_out_repeat')
async def event_handler_booking_time_out_repeat(booking):
    await _event_handler_booking_time_out_repeat(event_emitter=event_emitter, booking=booking)


@event_emitter.ee.on('pay_booking')
async def event_handler_pay_booking(booking, user, old_group_status):
    await _event_handler_pay_booking(
        event_emitter=event_emitter,
        booking=booking,
        user=user,
        old_group_status=old_group_status,
    )


@event_emitter.ee.on('booking_payed')
async def event_handler_booking_payed(booking, user, old_group_status):
    await _event_handler_booking_payed(
        event_emitter=event_emitter,
        booking=booking,
        user=user,
        old_group_status=old_group_status,
    )


@event_emitter.ee.on('booking_created')
async def event_handler_booking_created(
        booking,
        user: User | None = None,
):
    await _event_handler_booking_created(
        event_emitter=event_emitter,
        booking=booking,
        user=user,
    )


@event_emitter.ee.on('personal_filled')
async def event_handler_personal_filled(
        booking,
        user: User,
        old_group_status: str,
):
    await _event_handler_personal_filled(
        event_emitter=event_emitter,
        booking=booking,
        user=user,
        old_group_status=old_group_status,
    )


@event_emitter.ee.on('accept_contract')
async def event_handler_accept_contract(
        booking,
        user: User,
        city: str | None,
):
    await _event_handler_accept_contract(
        event_emitter=event_emitter,
        booking=booking,
        user=user,
        city=city,
    )


@event_emitter.ee.on('change_status')
async def event_handler_change_status(
        booking,
        user: User | None,
        old_group_status: str,
):
    if old_group_status == booking.amocrm_substage:
        return

    await _event_handler_change_status(
        event_emitter=event_emitter,
        booking=booking,
        user=user,
        old_group_status=old_group_status,
    )


@event_emitter.ee.on('extend_free_booking')
async def event_handler_extend_free_booking(
        booking,
        user: User | None,
        old_group_status: str,
):

    await _event_handler_extend_free_booking(
        event_emitter=event_emitter,
        booking=booking,
        user=user,
        old_group_status=old_group_status,
    )

@event_emitter.ee.on('cancel_loyalty_reward_from_booking')
async def event_handler_cancel_loyalty_reward_from_booking(booking, comment):

    await _event_handler_cancel_loyalty_reward_from_booking(
        event_emitter=event_emitter,
        booking=booking,
        comment=comment,
    )


@event_emitter.ee.on('error')
def on_error(message):
    print("Error", message)
