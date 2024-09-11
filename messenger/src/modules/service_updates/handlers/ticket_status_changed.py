from sl_messenger_protobuf.main_pb2 import ServerMessage
from sl_messenger_protobuf.responses_pb2 import TicketStatusChangedUpdate

from src.core.types import ConnectionId
from src.entities.tickets import TicketStatus
from src.entities.users import Role
from src.exceptions import InternalError
from src.modules.chat.serializers.converters import ticket_status_to_pb
from src.modules.push_notifications.interface import PushNotificationsRMQOpts, SendPushQueueMessage
from src.modules.service_updates.entities import TicketStatusChanged
from src.modules.service_updates.handlers.base import BaseUpdateHandler


class TicketStatusChangedUpdateHandler(BaseUpdateHandler[TicketStatusChanged], update_type=TicketStatusChanged):
    async def handle(self, cid: ConnectionId | None, update: TicketStatusChanged) -> None:
        online_supervisors = await self.presence_srvc.get_active_users(
            Role.SUPERVISOR,
            activity_time=self.settings.updates_broadcast_extended_activity_time,
        )
        send_updates_to = {supervisor.user_id for supervisor in online_supervisors}
        send_updates_to.add(update.changed_by_user_id)

        async with self.storage_srvc.connect() as db_conn:
            ticket = await db_conn.tickets.get_ticket_by_id(update.ticket_id)
            if not ticket:
                raise InternalError(f"Ticket with id {update.ticket_id} not found")

            send_updates_to.add(ticket.created_by)

        await self._broadcast_updates(
            ServerMessage(
                ticket_status_changed_update=TicketStatusChangedUpdate(
                    old_status=ticket_status_to_pb(update.old_status),
                    new_status=ticket_status_to_pb(update.new_status),
                    ticket_id=update.ticket_id,
                    changed_by_user_id=update.changed_by_user_id,
                ),
            ),
            user_ids=list(send_updates_to),
            skip_connection=None,
        )

        await self._send_push_notifications(update)

    async def _send_push_notifications(self, update: TicketStatusChanged) -> None:
        send_updates_on_transitions = (
            (TicketStatus.NEW, TicketStatus.IN_PROGRESS),
            (TicketStatus.IN_PROGRESS, TicketStatus.SOLVED),
        )

        if (update.old_status, update.new_status) not in send_updates_on_transitions:
            return

        await self.rabbitmq_publisher[PushNotificationsRMQOpts].publish_update(
            SendPushQueueMessage(source_event=update),
        )
