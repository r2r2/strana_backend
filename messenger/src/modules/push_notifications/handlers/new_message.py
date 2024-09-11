import base64

from sl_messenger_protobuf.messages_pb2 import MessageContent as PBMessageContent
from sl_messenger_protobuf.notifications_pb2 import (
    NewMessageNotification,
    NotificationMatchData,
    NotificationTicketData,
    NotificationUserData,
    PushNotificationContent,
)
from web_pusher import ClientCredentials
from web_pusher.enums import Urgency

from src.controllers.push_notifications import PushNotificationsController
from src.entities.users import Role
from src.exceptions import InternalError
from src.modules.chat.serializers.converters import role_to_pb
from src.modules.service_updates.entities import MessageSentToChat
from src.providers.time import timestamp_now

from .base import BaseUpdateHandler, PreparedPushNotification

MESSAGE_NOTIFICATION_TTL = 86400  # 1 day


class NewMessageNotificationsSender(BaseUpdateHandler[MessageSentToChat], update_type=MessageSentToChat):
    async def handle(self, update: MessageSentToChat) -> list[PreparedPushNotification]:
        result = []

        message_content = PBMessageContent.FromString(base64.b64decode(update.content_raw.encode()))

        referenced_users = PushNotificationsController.extract_referenced_user_ids_from_content(message_content)

        if update.sender_id:
            referenced_users.append(update.sender_id)

        async with self.storage_srvc.connect() as conn:
            users_in_chat = await conn.chats.get_users_in_chat(update.chat_id)

            chat_info = await conn.chats.get_chat_by_id(update.chat_id)
            if not chat_info:
                raise InternalError(f"Chat with id {update.chat_id} was not found")

            if chat_info.match_id:
                match_info = await conn.matches.get_match_by_id(chat_info.match_id)
                if not match_info:
                    raise InternalError(f"Match with id {chat_info.match_id} was not found")

                match_data = NotificationMatchData(
                    id=match_info.sportlevel_id,
                    team_a_name_ru=match_info.team_a.name_ru,
                    team_b_name_ru=match_info.team_b.name_ru,
                    team_a_name_en=match_info.team_a.name_en,
                    team_b_name_en=match_info.team_b.name_en,
                )
            else:
                match_data = None

            if not referenced_users:
                ref_user_data = []
            else:
                ref_user_data = [
                    NotificationUserData(
                        id=user.sportlevel_id,
                        name=user.name,
                        role=role_to_pb(user.role),
                        scout_number=user.scout_number,
                    )
                    for user in await conn.users.get_by_ids(referenced_users)
                ]

            if chat_info.chat_meta.assigned_ticket_id:
                ticket_data = NotificationTicketData(id=chat_info.chat_meta.assigned_ticket_id)
            else:
                ticket_data = None

            for recipient in {
                user for user in users_in_chat if user.user_id not in {update.sender_id, update.initiator_id}
            }:
                push_configs = await self.get_active_configs_for_user(db=conn, user_id=recipient.user_id)
                self.logger.debug(f"Push configs for user {recipient.user_id}: {push_configs}")
                if not push_configs:
                    continue

                notification_content = PushNotificationContent(
                    created_at=timestamp_now(),
                    new_message=NewMessageNotification(
                        id=update.message_id,
                        chat_id=update.chat_id,
                        sent_at=update.msg_created_at,
                        sender_id=update.sender_id,
                        content=message_content,
                        match_data=match_data,
                        ticket_data=ticket_data,
                        user_data=ref_user_data,
                    ),
                )

                self._truncate_message(notification_content)
                if _should_anonymize_users := recipient.user_role != Role.SUPERVISOR:
                    self._anonymize_message(notification_content)

                for config in push_configs:
                    result.append(
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

        return result
