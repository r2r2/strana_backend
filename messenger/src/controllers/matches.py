from fastapi import Depends, HTTPException, status
from sl_messenger_protobuf.messages_pb2 import ChatCreatedNotificationContent, MessageContent

from src.api.http.serializers.chats import ChatOptionsResponse, OptionsExistingChatResponse, OptionsScoutResponse
from src.api.http.serializers.matches import (
    MatchListResponse,
    MatchResponse,
    StartChatWithScoutResponse,
)
from src.controllers.messages import MessagesController
from src.controllers.permissions import PermissionsController
from src.controllers.unread_counters import UnreadCountersController
from src.core.common.rabbitmq import RabbitMQPublisherFactoryProto
from src.core.common.utility import find_by_predicate
from src.core.di import Injected
from src.entities.chats import ChatMeta
from src.entities.matches import ChatType, MatchFilters, MatchState
from src.entities.users import AuthPayload, Role
from src.modules.presence.interface import PresenceServiceProto
from src.modules.service_updates import ServiceUpdatesRMQOpts
from src.modules.service_updates.entities import ChatCreated, MatchCreated, UserDataChanged
from src.modules.sportlevel.interface import SportlevelServiceProto
from src.modules.storage.dependencies import inject_storage
from src.modules.storage.interface import StorageProtocol


class MatchesController:
    def __init__(
        self,
        presence_service: PresenceServiceProto = Injected[PresenceServiceProto],
        rabbitmq_publisher: RabbitMQPublisherFactoryProto = Injected[RabbitMQPublisherFactoryProto],
        sportlevel: SportlevelServiceProto = Injected[SportlevelServiceProto],
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
        self._sportlevel = sportlevel
        self._unread_counters = unread_counters

    async def get_match(
        self,
        match_id: int,
        user: AuthPayload,
        try_index: bool | None,
    ) -> MatchResponse:
        roles_allowed_to_index = (Role.BOOKMAKER, Role.SUPERVISOR)
        if try_index is None:
            try_index = user.role in roles_allowed_to_index

        if try_index and user.role not in roles_allowed_to_index:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You don't have permission to index match data")

        match_info = await self._storage.matches.get_match_info(
            user_id=user.id,
            user_role=user.role,
            lang=user.lang,
            match_id=match_id,
        )
        if not match_info:
            if not (_is_exists := await self._storage.matches.get_match_by_id(sportlevel_id=match_id)) and try_index:
                # Match is already exists in DB, but not accessible for user
                await self._try_index_match(match_id=match_id)
                return await self.get_match(match_id=match_id, user=user, try_index=False)

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found or not accessible",
            )

        return MatchResponse(
            **match_info.model_dump(),
            unread_count=await self._unread_counters.get_unread_count_by_match_id(user_id=user.id, match_id=match_id),
        )

    async def _try_index_match(self, match_id: int) -> None:
        sl_data = await self._sportlevel.get_match_by_id(match_id=match_id)
        if not sl_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found in SL and in DB",
            )

        await self._storage.matches.create_match_with_scouts(sl_data)
        await self._storage.commit_transaction()
        await self._updates_publisher.publish_update(MatchCreated(payload=sl_data))

        for scout in sl_data.scouts:
            user = await self._storage.users.get_by_id(user_id=scout.id)
            if not user:
                await self._updates_publisher.publish_update(
                    UserDataChanged(
                        user_id=scout.id,
                        scout_number=scout.scout_number,
                        name=scout.name,
                        role=Role.SCOUT,
                    ),
                )

    async def get_matches(
        self,
        user: AuthPayload,
        filters: MatchFilters,
        offset: int,
        limit: int,
    ) -> list[MatchResponse]:
        matches = await self._storage.matches.get_matches(
            user_id=user.id,
            user_role=user.role,
            lang=user.lang,
            filters=filters,
            limit=limit,
            offset=offset,
        )

        unread_counters = await self._unread_counters.get_unread_count_by_match_ids(
            user_id=user.id,
            match_ids=[m.sportlevel_id for m in matches],
        )
        match_responses = []
        for match in matches:
            if user.role == Role.SCOUT and match.chat_id:
                mem_d = await self._storage.chats.get_chat_membership_details(chat_id=match.chat_id, user_id=user.id)
                if mem_d and mem_d.is_archive_member:
                    match.state = MatchState.ARCHIVED

            match_responses.append(
                MatchResponse(
                    **match.model_dump(),
                    unread_count=unread_counters[match.sportlevel_id],
                ),
            )

        return match_responses

    async def get_matches_list(
        self,
        user: AuthPayload,
        filters: MatchFilters,
        offset: int,
        limit: int,
    ) -> list[MatchListResponse]:
        matches = await self._storage.matches.get_matches_list(
            user_id=user.id,
            user_role=user.role,
            lang=user.lang,
            filters=filters,
            limit=limit,
            offset=offset,
        )

        return [MatchListResponse(**match.model_dump()) for match in matches]

    async def start_chat(
        self,
        match_id: int,
        user: AuthPayload,
        scout_user_id: int,
    ) -> StartChatWithScoutResponse:
        match_info = await self._storage.matches.get_match_by_id(sportlevel_id=match_id)
        if not match_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found",
            )

        if not match_info.state.is_active:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Match is not active",
            )

        match_scout = await self._storage.matches.get_match_scout(match_id=match_id, scout_id=scout_user_id)
        if not match_scout:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The specified scout id is not linked to the match",
            )

        if await self._storage.chats.is_chat_with_scout_exists(
            match_id=match_id,
            scout_id=scout_user_id,
            bookmaker_id=user.id,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Chat with this scout already exists",
            )

        chat = await self._storage.chats.create_chat(
            match_id=match_id,
            chat_type=ChatType.MATCH,
            meta=ChatMeta(),
        )

        await self._storage.chats.add_user_to_chat(
            user_id=user.id,
            chat_id=chat.id,
            role=Role.BOOKMAKER,
            is_primary_member=True,
            has_write_permission=True,
            has_read_permission=True,
        )

        await self._storage.chats.add_user_to_chat(
            user_id=scout_user_id,
            chat_id=chat.id,
            role=Role.SCOUT,
            is_primary_member=True,
            has_write_permission=True,
            has_read_permission=True,
        )

        await self._unread_counters.set_unread_count_by_chat_id(user_id=user.id, chat_id=chat.id, value=0)
        await self._unread_counters.set_unread_count_by_chat_id(user_id=scout_user_id, chat_id=chat.id, value=0)

        message = await self._messages.create_message(
            chat_id=chat.id,
            content=MessageContent(
                chat_created_notification=ChatCreatedNotificationContent(
                    created_by_user_id=user.id,
                ),
            ),
            initiator_id=user.id,
        )
        await self._storage.chats.update_scout_membership(
            chat_id=chat.id,
            scout_id=scout_user_id,
            first_available_message_id=message.id,
        )

        await self._storage.commit_transaction()

        await self._updates_publisher.publish_update(
            ChatCreated(
                chat_id=chat.id,
                created_by_user_id=user.id,
                match_id=chat.match_id,
                chat_type=ChatType.MATCH,
            ),
        )

        return StartChatWithScoutResponse(chat_id=chat.id)

    async def get_chat_options(
        self,
        match_id: int,
        user: AuthPayload,
    ) -> ChatOptionsResponse:
        result = ChatOptionsResponse()

        match user.role:
            case Role.SCOUT:
                match_scouts = await self._storage.matches.get_match_scouts(match_id=match_id)

                if scout := find_by_predicate(match_scouts, lambda scout: scout.id == user.id):
                    result.current_scouts.append(
                        OptionsScoutResponse(
                            user_id=user.id,
                            is_main_scout=scout.is_main_scout,
                        ),
                    )

            case Role.BOOKMAKER:
                all_chats = await self._storage.chats.get_all_chats_by_match(
                    match_id=match_id,
                    chat_types=[ChatType.MATCH],
                )
                match_scouts = await self._storage.matches.get_match_scouts(match_id=match_id)

                result.current_scouts = [
                    OptionsScoutResponse(
                        user_id=scout.id,
                        is_main_scout=scout.is_main_scout,
                    )
                    for scout in match_scouts
                ]

                for match_scout in match_scouts:
                    if chat := find_by_predicate(
                        all_chats,
                        lambda chat: match_scout.id in [memb.user_id for memb in chat.primary_members]  # noqa: B023
                        and user.id in [memb.user_id for memb in chat.primary_members],
                    ):
                        result.existing_chats.append(
                            OptionsExistingChatResponse(
                                chat_id=chat.id,
                                user_id=match_scout.id,
                            ),
                        )
                    else:
                        result.available_chats.append(match_scout.id)

            case _:
                ...

        return result
