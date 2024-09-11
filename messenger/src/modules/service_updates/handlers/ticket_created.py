from sl_messenger_protobuf.main_pb2 import ServerMessage
from sl_messenger_protobuf.responses_pb2 import TicketCreatedUpdate

from src.core.types import ConnectionId
from src.entities.users import Role
from src.exceptions import InternalError
from src.modules.push_notifications import PushNotificationsRMQOpts, SendPushQueueMessage
from src.modules.service_updates.entities import TicketCreated
from src.modules.service_updates.handlers.base import BaseUpdateHandler
from src.modules.telegram import NewTicketTgNotificationPayload


class TicketCreatedUpdateHandler(BaseUpdateHandler[TicketCreated], update_type=TicketCreated):
    async def handle(self, cid: ConnectionId | None, update: TicketCreated) -> None:
        online_supervisors = await self.presence_srvc.get_active_users(
            Role.SUPERVISOR,
            activity_time=self.settings.updates_broadcast_extended_activity_time,
        )
        online_supervisors_ids = [supervisor.user_id for supervisor in online_supervisors]

        await self._broadcast_updates(
            ServerMessage(
                ticket_created_update=TicketCreatedUpdate(
                    ticket_id=update.ticket_id,
                    match_id=update.match_id or 0,
                    created_by_user_id=update.created_by_user_id,
                ),
            ),
            user_ids=online_supervisors_ids,
        )

        await self.rabbitmq_publisher[PushNotificationsRMQOpts].publish_update(
            SendPushQueueMessage(source_event=update),
        )

        async with self.storage_srvc.connect() as db_conn:
            creator = await db_conn.users.get_by_id(user_id=update.created_by_user_id)
            if not creator:
                raise InternalError(f"User with id {update.created_by_user_id} not found")

        self.telegram_srvc.send_message(
            message=NewTicketTgNotificationPayload(
                ticket_id=update.ticket_id,
                match_id=update.match_id,
                chat_id=update.chat_id,
                created_by=creator.name,
            )
        )
