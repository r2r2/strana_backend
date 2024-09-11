from fastapi import Depends, HTTPException, status
from sl_messenger_protobuf.enums_pb2 import ChatCloseReason, ChatOpenReason
from sl_messenger_protobuf.messages_pb2 import (
    ChatClosedNotificationContent,
    ChatCreatedNotificationContent,
    ChatOpenedNotificationContent,
    MessageContent,
    UserJoinedChatNotificationContent,
    UserLeftChatNotificationContent,
)
from sl_messenger_protobuf.messages_pb2 import MessageContent as MessageContentPb

from src.api.http.serializers.chats import ChatResponse, UnreadCountResponse
from src.controllers.messages import MessagesController
from src.controllers.permissions import PermissionsController
from src.controllers.unread_counters import UnreadCountersController
from src.core.common.rabbitmq import RabbitMQPublisherFactoryProto
from src.core.di import Injected
from src.entities.chats import ChatMeta
from src.entities.matches import ChatType
from src.entities.messages import MessageDTO
from src.entities.users import AuthPayload, Role
from src.exceptions import InternalError
from src.modules.presence.interface import PresenceServiceProto
from src.modules.service_updates import ServiceUpdatesRMQOpts
from src.modules.service_updates.entities import ChatCreated
from src.modules.storage.dependencies import inject_storage
from src.modules.storage.interface import StorageProtocol


class ChatsController:
    def __init__(
        self,
        presence_service: PresenceServiceProto = Injected[PresenceServiceProto],
        rabbitmq_publisher: RabbitMQPublisherFactoryProto = Injected[RabbitMQPublisherFactoryProto],
        storage: StorageProtocol = Depends(inject_storage),
        permissions: PermissionsController = Depends(),
        messages: MessagesController = Depends(),
        unread_counters: UnreadCountersController = Depends(),
    ) -> None:
        self._storage = storage
        self._permissions = permissions
        self._updates_publisher = rabbitmq_publisher[ServiceUpdatesRMQOpts]
        self._presence = presence_service
        self._messages = messages
        self._unread_counters = unread_counters

    async def get_unread_count(self, user: AuthPayload) -> UnreadCountResponse:
        return UnreadCountResponse(
            unread=await self._unread_counters.get_total_unread_count(user_id=user.id),
        )

    async def close_chat(self, chat_id: int, user: AuthPayload) -> None:
        chat = await self._storage.chats.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Chat not found")

        if chat.is_closed:
            raise HTTPException(status.HTTP_409_CONFLICT, "Chat is already closed")

        if chat.type != ChatType.PERSONAL:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only personal chats can be closed")

        await self._storage.chats.close_chats(chat_ids=[chat_id])
        await self._storage.commit_transaction()

        await self._messages.create_message(
            chat_id=chat_id,
            content=MessageContentPb(
                chat_closed_notification=ChatClosedNotificationContent(
                    reason=ChatCloseReason.CHAT_CLOSE_REASON_INITIATED_BY_USER,
                ),
            ),
            sender_id=None,
            initiator_id=user.id,
        )

    async def open_chat(self, chat_id: int, user: AuthPayload) -> None:
        chat = await self._storage.chats.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Chat not found")

        if not chat.is_closed:
            raise HTTPException(status.HTTP_409_CONFLICT, "Chat is not closed")

        if chat.type != ChatType.PERSONAL:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only personal chats can be closed")

        await self._storage.chats.reopen_chat(chat_id=chat_id)
        await self._storage.commit_transaction()

        await self._messages.create_message(
            chat_id=chat_id,
            content=MessageContentPb(
                chat_opened_notification=ChatOpenedNotificationContent(
                    reason=ChatOpenReason.CHAT_OPEN_REASON_INITIATED_BY_USER,
                ),
            ),
            sender_id=None,
            initiator_id=user.id,
        )

    async def get_chat_messages(
        self,
        user: AuthPayload,
        chat_id: int,
        backwards: bool,
        limit: int,
        from_message_id: int | None,
    ) -> list[MessageDTO]:
        chat_access = await self._permissions.is_chat_accessible(
            chat_id=chat_id,
            user_id=user.id,
            user_role=user.role,
            storage=self._storage,
        )
        if not chat_access.is_accessible:
            raise HTTPException(status.HTTP_403_FORBIDDEN, chat_access.error_msg)

        from_message = from_message_id
        if (
            chat_access.first_available_message_id
            and from_message_id
            and from_message_id < chat_access.first_available_message_id
        ):
            from_message = chat_access.first_available_message_id

        return await self._storage.messages.get_messages(
            chat_id=chat_id,
            user_id=user.id,
            from_message_id=from_message,
            backwards=backwards,
            limit=limit,
            last_available_message_id=chat_access.last_available_message_id,
        )

    async def search_chats(
        self,
        user: AuthPayload,
        chat_type: ChatType | None,
        match_id: int | None,
        limit: int,
        offset: int,
    ) -> list[ChatResponse]:
        chats = await self._storage.chats.get_chats(
            user_id=user.id,
            user_role=user.role,
            chat_type=chat_type,
            match_id=match_id,
            limit=limit,
            offset=offset,
        )

        unread_counters = await self._unread_counters.get_unread_count_by_chat_ids(
            user_id=user.id,
            chat_ids=[chat.chat_id for chat in chats],
        )

        online_users_ids = {user.user_id for user in await self._presence.get_active_users()}

        for chat in chats:
            for member in chat.members or []:
                member.is_online = member.user_id in online_users_ids

        return [
            ChatResponse(
                **chat.dict(),
                unread_count=unread_counters[chat.chat_id],
            )
            for chat in chats
        ]

    async def get_chat(self, user: AuthPayload, chat_id: int) -> ChatResponse:
        chat = await self._storage.chats.get_chat(
            user_id=user.id,
            chat_id=chat_id,
            user_role=user.role,
        )
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        online_users_ids = {user.user_id for user in await self._presence.get_active_users()}

        if chat.members:
            for member in chat.members:
                member.is_online = member.user_id in online_users_ids

        return ChatResponse(
            **chat.dict(),
            unread_count=await self._unread_counters.get_unread_count_by_chat_id(
                user_id=user.id,
                chat_id=chat_id,
            ),
        )

    async def create_chat(
        self,
        user: AuthPayload,
        target_user_id: int,
    ) -> tuple[int, bool]:
        """
        Creates a chat between two users. If the chat already exists, returns its ID. Otherwise, creates a new chat.

        Returns a tuple of:
            chat_id: ID of the chat
            is_new: True if the chat was created, False if it already existed
        """
        if user.role != Role.SUPERVISOR:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Action is not permitted")

        target_user = await self._storage.users.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "User not found")

        if chat_id := await self._storage.chats.get_chat_id_between_users(user.id, target_user_id):
            return chat_id, False

        new_chat = await self._storage.chats.create_chat(
            match_id=None,
            chat_type=ChatType.PERSONAL,
            meta=ChatMeta(),
        )

        await self._storage.chats.add_user_to_chat(
            user_id=user.id,
            chat_id=new_chat.id,
            role=user.role,
            has_write_permission=True,
            has_read_permission=True,
            is_primary_member=True,
        )

        await self._storage.chats.add_user_to_chat(
            user_id=target_user_id,
            chat_id=new_chat.id,
            role=target_user.role,
            has_write_permission=True,
            has_read_permission=True,
            is_primary_member=True,
        )

        await self._unread_counters.set_unread_count_by_chat_id(
            user_id=user.id,
            chat_id=new_chat.id,
            value=1,
        )
        await self._unread_counters.set_unread_count_by_chat_id(
            user_id=target_user_id,
            chat_id=new_chat.id,
            value=1,
        )

        await self._storage.commit_transaction()

        await self._messages.create_message(
            chat_id=new_chat.id,
            content=MessageContent(
                chat_created_notification=ChatCreatedNotificationContent(created_by_user_id=user.id),
            ),
            do_not_increment_counter=True,
            initiator_id=user.id,
        )

        await self._updates_publisher.publish_update(
            ChatCreated(
                chat_id=new_chat.id,
                created_by_user_id=user.id,
                match_id=new_chat.match_id,
                chat_type=ChatType.PERSONAL,
            ),
        )

        return new_chat.id, True

    async def join_chat(
        self,
        chat_id: int,
        user: AuthPayload,
    ) -> None:
        chat = await self._storage.chats.get_chat_by_id(chat_id=chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        if chat.is_closed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chat is closed",
            )

        chat_access = await self._permissions.is_chat_accessible(
            chat_id=chat_id,
            user_id=user.id,
            user_role=user.role,
            storage=self._storage,
        )
        if not chat_access.is_accessible:
            raise HTTPException(status.HTTP_403_FORBIDDEN, chat_access.error_msg)

        if await self._storage.chats.is_user_in_chat(chat_id=chat_id, user_id=user.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The user is already a member of the chat room",
            )

        match chat.type:
            case ChatType.MATCH:
                # Match chat, only bookmakers can join
                if user.role != Role.BOOKMAKER:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Action is not permitted",
                    )

                # The second bookmaker is trying to join the chat
                await self._storage.chats.add_user_to_chat(
                    user_id=user.id,
                    chat_id=chat_id,
                    role=user.role,
                    has_write_permission=True,
                    has_read_permission=False,
                    is_primary_member=False,
                )

                if not chat.match_id:
                    raise InternalError("Match ID is not set for match chat")

                await self._unread_counters.clean_unread_count_by_chat_id(user_id=user.id, chat_id=chat_id)
                await self._unread_counters.clean_unread_count_by_match_id(user_id=user.id, match_id=chat.match_id)
                unread_count = await self._unread_counters.get_unread_count_by_chat_id(user_id=user.id, chat_id=chat_id)
                if unread_count:
                    await self._unread_counters.update_total_unread_count(user_id=user.id, update_by=unread_count)

                await self._storage.commit_transaction()

                await self._messages.create_message(
                    chat_id=chat_id,
                    content=MessageContentPb(
                        user_joined_chat_notification=UserJoinedChatNotificationContent(user_id=user.id),
                    ),
                    initiator_id=user.id,
                )

            case ChatType.TICKET | ChatType.PERSONAL:
                # Ticket chat, impossible to join
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Chat is not joinable",
                )

    async def leave_chat(
        self,
        chat_id: int,
        user: AuthPayload,
    ) -> None:
        chat = await self._storage.chats.get_chat_by_id(chat_id=chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        if chat.is_closed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chat is closed",
            )

        membership = await self._storage.chats.get_chat_membership_details(
            user_id=user.id,
            chat_id=chat_id,
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is not a member of the chat",
            )

        if chat.type != ChatType.PERSONAL and membership.is_primary_member:
            # User can leave only general chat or specific chat as a secondary member
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Action is not permitted",
            )

        await self._storage.chats.remove_user_from_chat(user_id=user.id, chat_id=chat_id)
        await self._storage.commit_transaction()

        await self._unread_counters.clean_unread_count_by_chat_id(user_id=user.id, chat_id=chat_id)
        if chat.match_id:
            await self._unread_counters.clean_unread_count_by_match_id(user_id=user.id, match_id=chat.match_id)

        unread_count = await self._unread_counters.get_unread_count_by_chat_id(user_id=user.id, chat_id=chat_id)
        if unread_count:
            await self._unread_counters.update_total_unread_count(user_id=user.id, update_by=-unread_count)

        await self._messages.create_message(
            chat_id=chat_id,
            content=MessageContentPb(
                user_left_chat_notification=UserLeftChatNotificationContent(user_id=user.id),
            ),
            initiator_id=user.id,
        )
