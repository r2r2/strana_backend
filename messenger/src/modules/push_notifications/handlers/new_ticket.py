from sl_messenger_protobuf.notifications_pb2 import NewTicketNotification, NotificationUserData, PushNotificationContent
from web_pusher import ClientCredentials
from web_pusher.enums import Urgency

from src.entities.users import Role
from src.exceptions import InternalError
from src.modules.chat.serializers.converters import role_to_pb
from src.modules.service_updates.entities import TicketCreated
from src.providers.time import timestamp_now

from .base import BaseUpdateHandler, PreparedPushNotification

TICKET_NOTIFICATION_TTL = 86400 * 7  # 7 days


class NewTicketNotificationsSender(BaseUpdateHandler[TicketCreated], update_type=TicketCreated):
    async def handle(self, update: TicketCreated) -> list[PreparedPushNotification]:
        results = []

        async with self.storage_srvc.connect() as conn:
            supervisors, users_count = await conn.users.search(filter_by_role=Role.SUPERVISOR)
            ticket_author = await conn.users.get_by_id(update.created_by_user_id)

            if not ticket_author:
                raise InternalError(
                    f"User with id {update.created_by_user_id} was not found",
                )

            if not users_count:
                return []

            notification_content = PushNotificationContent(
                created_at=timestamp_now(),
                new_ticket=NewTicketNotification(
                    ticket_id=update.ticket_id,
                    match_id=update.match_id,
                    chat_id=update.chat_id,
                    created_by=NotificationUserData(
                        id=ticket_author.sportlevel_id,
                        role=role_to_pb(ticket_author.role),
                        name=ticket_author.name,
                        scout_number=ticket_author.scout_number,
                    ),
                ),
            )

            for user in supervisors:
                if not (push_configs := await self.get_active_configs_for_user(db=conn, user_id=user.sportlevel_id)):
                    continue

                self.logger.debug(f"Push configs for user {user.sportlevel_id}: {push_configs}")

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
                            ttl=TICKET_NOTIFICATION_TTL,
                            urgency=Urgency.HIGH,
                        )
                    )

            await conn.commit_transaction()

        return results
