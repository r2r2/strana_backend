from common.event_emitter.client import EventEmitter
from src.meetings.event_emitter_callbacks import _event_handler_meeting_created, _event_handler_meeting_status_changed
from src.meetings.repos import MeetingStatus

from src.users.repos import User

meeting_event_emitter = EventEmitter()


@meeting_event_emitter.ee.on('meeting_created')
async def event_handler_meeting_created(booking, new_status: MeetingStatus, user: User | None = None,):
    await _event_handler_meeting_created(
        event_emitter=meeting_event_emitter, booking=booking, new_status=new_status, user=user
    )


@meeting_event_emitter.ee.on('meeting_status_changed')
async def event_handler_meeting_status_changed(
        booking,
        new_status: MeetingStatus | None,
        old_status: MeetingStatus | None,
        user: User | None = None,
):
    if new_status != old_status:
        await _event_handler_meeting_status_changed(
            event_emitter=meeting_event_emitter,
            booking=booking,
            new_status=new_status,
            old_status=old_status,
            user=user,
        )


@meeting_event_emitter.ee.on('error')
def on_error(message):
    print("Error", message)
