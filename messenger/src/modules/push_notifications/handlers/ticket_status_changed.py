from sl_messenger_protobuf.notifications_pb2 import (
    NotificationUserData,
    PushNotificationContent,
    TicketStatusChangedNotification,
)
from web_pusher import ClientCredentials
from web_pusher.enums import Urgency

from src.entities.users import Role
from src.exceptions import InternalError
from src.modules.chat.serializers.converters import role_to_pb, ticket_status_to_pb
from src.modules.service_updates.entities import TicketStatusChanged
from src.providers.time import timestamp_now

from .base import BaseUpdateHandler, PreparedPushNotification

MESSAGE_NOTIFICATION_TTL = 86400  # 1 day


class TicketStatusChangedNotificationsSender(BaseUpdateHandler[TicketStatusChanged], update_type=TicketStatusChanged):
    async def handle(self, update: TicketStatusChanged) -> list[PreparedPushNotification]:
        results = []

        async with self.storage_srvc.connect() as conn:
            ticket = await conn.tickets.get_ticket_by_id(update.ticket_id)
            changed_by_user = await conn.users.get_by_id(update.changed_by_user_id)

            if not ticket:
                raise InternalError(f"Ticket with id {update.ticket_id} not found")

            if not changed_by_user:
                raise InternalError(f"User with id {update.changed_by_user_id} not found")

            users_in_chat = await conn.chats.get_users_in_chat(ticket.chat_id)

            if ticket.created_from_chat_id:
                created_from_chat = await conn.chats.get_chat_by_id(ticket.created_from_chat_id)
                if not created_from_chat:
                    raise InternalError(f"Chat with id {ticket.created_from_chat_id} not found")

                match_id = created_from_chat.match_id
            else:
                match_id = None

            for recipient in {user for user in users_in_chat if user.user_id != update.changed_by_user_id}:
                push_configs = await self.get_active_configs_for_user(db=conn, user_id=recipient.user_id)
                self.logger.debug(f"Push configs for user {recipient.user_id}: {push_configs}")
                if not push_configs:
                    continue

                notification_content = PushNotificationContent(
                    created_at=timestamp_now(),
                    ticket_status_changed=TicketStatusChangedNotification(
                        ticket_id=ticket.id,
                        status=ticket_status_to_pb(update.new_status),
                        old_status=ticket_status_to_pb(update.old_status),
                        changed_by=NotificationUserData(
                            id=changed_by_user.sportlevel_id,
                            name=changed_by_user.name,
                            role=role_to_pb(changed_by_user.role),
                            scout_number=changed_by_user.scout_number,
                        ),
                        chat_id=ticket.chat_id,
                        match_id=match_id,
                    ),
                )

                if _should_anonymize_users := recipient.user_role != Role.SUPERVISOR:
                    self._anonymize_message(notification_content)

                for config in push_configs:
                    results.append(
                        PreparedPushNotification(
                            recipient_user_id=config.user_id,
                            content=notification_content,
                            client_credentials=ClientCredentials.parse_from_dict(
                                {
                                    "endpoint": config.endpoint,
                                    "keys": config.keys,
                                }
                            ),
                            device_id=config.device_id,
                            ttl=MESSAGE_NOTIFICATION_TTL,
                            urgency=Urgency.HIGH,
                        )
                    )

            await conn.commit_transaction()

        return results
