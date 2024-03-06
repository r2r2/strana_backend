from common.event_emitter.client import EventEmitter
from src.mortgage.event_emitter_callbacks import _event_handler_ticket_change_status, _event_handler_ticket_create

mortage_event_emitter = EventEmitter()


@mortage_event_emitter.ee.on('ticket_change_status')
async def event_handler_ticket_change_status(
        booking_id,
        user,
        mortgage_ticket_inform,
):
    await _event_handler_ticket_change_status(
        event_emitter=mortage_event_emitter,
        booking_id=booking_id,
        user=user,
        mortgage_ticket_inform=mortgage_ticket_inform,
    )


@mortage_event_emitter.ee.on('ticket_create')
async def event_handler_ticket_create(
        booking_id,
        user,
        mortgage_ticket_inform,
):
    await _event_handler_ticket_create(
        event_emitter=mortage_event_emitter,
        booking_id=booking_id,
        user=user,
        mortgage_ticket_inform=mortgage_ticket_inform,
    )


@mortage_event_emitter.ee.on('error')
def on_error(message):
    print("Error", message)
