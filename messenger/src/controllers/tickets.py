from fastapi import Depends, HTTPException, status
from sl_messenger_protobuf.messages_pb2 import (
    MessageContent,
    RelatedTicketCreatedNotificationContent,
    TextContent,
    TicketClosedNotificationContent,
    TicketFirstMessageNotificationContent,
    TicketStatusChangedNotificationContent,
    UserJoinedChatNotificationContent,
)

from src.api.http.serializers.tickets import CreateTicketResponse, TicketInfo, TicketStatusFilter
from src.controllers.messages import MessagesController
from src.controllers.unread_counters import UnreadCountersController
from src.core.common.rabbitmq import RabbitMQPublisherFactoryProto
from src.core.di import Injected
from src.entities.chats import ChatMeta
from src.entities.matches import ChatType
from src.entities.tickets import TicketCloseReason, TicketFilters, TicketStatus
from src.entities.users import AuthPayload, Role
from src.exceptions import InternalError
from src.modules.chat.serializers.converters import ticket_status_to_pb
from src.modules.presence.interface import PresenceServiceProto
from src.modules.service_updates import ServiceUpdatesRMQOpts
from src.modules.service_updates.entities import ChatCreated, TicketCreated, TicketStatusChanged
from src.modules.storage.dependencies import inject_storage
from src.modules.storage.interface import StorageProtocol
from src.modules.storage.models import Chat, Ticket


class TicketsController:
    def __init__(
        self,
        rabbitmq_publisher: RabbitMQPublisherFactoryProto = Injected[RabbitMQPublisherFactoryProto],
        presence_service: PresenceServiceProto = Injected[PresenceServiceProto],
        storage: StorageProtocol = Depends(inject_storage),
        messages: MessagesController = Depends(),
        unread_counters: UnreadCountersController = Depends(),
    ) -> None:
        self._messages = messages
        self._storage = storage
        self._presence = presence_service
        self._updates_publisher = rabbitmq_publisher[ServiceUpdatesRMQOpts]
        self._unread_counters = unread_counters

    async def search_tickets(
        self,
        user: AuthPayload,
        status: TicketStatusFilter | None,
        filters: TicketFilters,
        limit: int,
        offset: int,
    ) -> tuple[list[TicketInfo], int]:
        result, total = await self._storage.tickets.search_tickets(
            user_id=user.id,
            user_role=user.role,
            status=status,
            lang=user.lang,
            filters=filters,
            limit=limit,
            offset=offset,
        )

        unread_counters = await self._unread_counters.get_unread_count_by_chat_ids(
            user_id=user.id,
            chat_ids=[ticket.chat_info.chat_id for ticket in result],
        )

        online_users = {user.user_id for user in await self._presence.get_active_users()}

        for ticket in result:
            ticket.chat_info.unread_count = unread_counters[ticket.chat_info.chat_id]
            for member in ticket.chat_info.members or []:
                member.is_online = member.user_id in online_users

        return result, total

    async def get_ticket_details(self, user: AuthPayload, ticket_id: int) -> TicketInfo | None:
        details = await self._storage.tickets.get_ticket_detailed(
            user_id=user.id,
            user_role=user.role,
            lang=user.lang,
            ticket_id=ticket_id,
        )
        if not details:
            return None

        online_users = {user.user_id for user in await self._presence.get_active_users()}

        details.chat_info.unread_count = await self._unread_counters.get_unread_count_by_chat_id(
            user_id=user.id,
            chat_id=details.chat_info.chat_id,
        )

        for member in details.chat_info.members or []:
            member.is_online = member.user_id in online_users

        return details

    async def take_into_work(self, ticket: Ticket, user: AuthPayload) -> None:
        if ticket.status != TicketStatus.NEW:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Ticket status is not TicketStatus.NEW",
            )

        if ticket.assigned_to_user_id and ticket.assigned_to_user_id != user.id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Ticket is assigned to user {ticket.assigned_to_user_id}",
            )

        await self._storage.tickets.update_ticket_status(
            ticket=ticket,
            new_status=TicketStatus.IN_PROGRESS,
            updated_by=user.id,
        )

        await self._storage.chats.add_user_to_chat(
            user_id=user.id,
            chat_id=ticket.chat_id,
            role=Role.SUPERVISOR,
            is_primary_member=True,
            has_read_permission=True,
            has_write_permission=True,
        )

        chat_info = await self._storage.chats.get_chat_by_id(ticket.chat_id)
        if not chat_info:
            raise InternalError(f"Chat {ticket.chat_id} not found")

        if chat_info.match_id:
            await self._unread_counters.clean_unread_count_by_match_id(user_id=user.id, match_id=chat_info.match_id)

        await self._unread_counters.clean_unread_count_by_chat_id(user_id=user.id, chat_id=ticket.chat_id)
        unread_count = await self._unread_counters.get_unread_count_by_chat_id(user_id=user.id, chat_id=ticket.chat_id)
        if unread_count:
            await self._unread_counters.update_total_unread_count(user_id=user.id, update_by=unread_count)

        await self._storage.commit_transaction()

        await self._messages.create_message(
            chat_id=ticket.chat_id,
            content=MessageContent(
                user_joined_chat_notification=UserJoinedChatNotificationContent(user_id=user.id),
            ),
            initiator_id=user.id,
        )

        await self._storage.tickets.assign_to_user(ticket_id=ticket.id, user_id=user.id)

        await self._storage.commit_transaction()

        await self._notify_ticket_status_changed(
            ticket_id=ticket.id,
            old_status=TicketStatus.NEW,
            new_status=TicketStatus.IN_PROGRESS,
            changed_by=user.id,
        )

    async def close_ticket(
        self,
        ticket: Ticket,
        user: AuthPayload,
        comment: str,
        close_reason: TicketCloseReason,
    ) -> None:
        if ticket.status not in (TicketStatus.IN_PROGRESS, TicketStatus.NEW):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Ticket status is not one of (TicketStatus.IN_PROGRESS, TicketStatus.NEW)",
            )

        if ticket.assigned_to_user_id and ticket.assigned_to_user_id != user.id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Ticket is assigned to user {ticket.assigned_to_user_id}",
            )

        old_status = ticket.status

        await self._storage.tickets.close_ticket(
            ticket=ticket,
            comment=comment,
            reason=close_reason,
            updated_by=user.id,
        )

        await self._storage.commit_transaction()

        await self._messages.create_message(
            chat_id=ticket.chat_id,
            content=MessageContent(
                ticket_closed_notification=TicketClosedNotificationContent(
                    ticket_id=ticket.id,
                    ticket_chat_id=ticket.chat_id,
                    closed_by_user_id=user.id,
                ),
            ),
            initiator_id=user.id,
        )

        if created_from_chat := ticket.created_from_chat_id:
            await self._messages.create_message(
                chat_id=created_from_chat,
                content=MessageContent(
                    ticket_closed_notification=TicketClosedNotificationContent(
                        ticket_id=ticket.id,
                        ticket_chat_id=ticket.chat_id,
                        closed_by_user_id=user.id,
                    ),
                ),
                initiator_id=user.id,
            )

        await self._notify_ticket_status_changed(
            ticket_id=ticket.id,
            old_status=old_status,
            new_status=TicketStatus.SOLVED,
            changed_by=user.id,
        )

    async def confirm_ticket(self, ticket: Ticket, user: AuthPayload) -> None:
        if user.role == Role.SUPERVISOR:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Supervisor cannot confirm a ticket")

        if ticket.status != TicketStatus.SOLVED:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Ticket status is not SOLVED")

        if not await self._storage.chats.is_user_in_chat(chat_id=ticket.chat_id, user_id=user.id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "User has no access to the ticket")

        await self._storage.tickets.update_ticket_status(
            ticket=ticket,
            new_status=TicketStatus.CONFIRMED,
            updated_by=user.id,
        )

        await self._storage.commit_transaction()

        await self._notify_ticket_status_changed(
            ticket_id=ticket.id,
            old_status=TicketStatus.SOLVED,
            new_status=TicketStatus.CONFIRMED,
            changed_by=user.id,
        )

    async def reopen_ticket(self, ticket: Ticket, user: AuthPayload) -> None:
        if user.role == Role.SUPERVISOR:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Supervisor cannot reopen a ticket")

        if ticket.status != TicketStatus.SOLVED:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Ticket status is not TicketStatus.SOLVED")

        if not await self._storage.chats.is_user_in_chat(chat_id=ticket.chat_id, user_id=user.id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "User has no access to the ticket")

        await self._storage.tickets.update_ticket_status(
            ticket=ticket,
            new_status=TicketStatus.IN_PROGRESS,
            updated_by=user.id,
        )

        await self._storage.commit_transaction()

        await self._messages.create_message(
            chat_id=ticket.chat_id,
            content=MessageContent(
                ticket_status_changed_notification=TicketStatusChangedNotificationContent(
                    ticket_id=ticket.id,
                    status=ticket_status_to_pb(TicketStatus.IN_PROGRESS),
                ),
            ),
            initiator_id=user.id,
        )

        await self._notify_ticket_status_changed(
            ticket_id=ticket.id,
            old_status=TicketStatus.SOLVED,
            new_status=TicketStatus.IN_PROGRESS,
            changed_by=user.id,
        )

    async def create_ticket(
        self,
        user: AuthPayload,
        match_id: int | None,
        created_from_chat_id: int | None,
        message: str,
    ) -> CreateTicketResponse:
        if match_id:
            await self._validate_match_info(match_id=match_id)

        if not created_from_chat_id:
            return await self._create_ticket_without_source_chat(user=user, match_id=match_id, message=message)

        created_from_chat = await self._storage.chats.get_chat_by_id(created_from_chat_id)
        if not created_from_chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        await self._check_able_to_create_ticket_for_match(
            user=user,
            match_id=match_id,
            chat_id=created_from_chat_id,
        )

        match created_from_chat.type:
            case ChatType.MATCH:
                related_chat = await self._create_chat_for_ticket_from_match(
                    user=user,
                    created_from_chat=created_from_chat,
                )

            case _:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="It is impossible to create a ticket for this chat",
                )

        ticket = await self._storage.tickets.create_ticket(
            created_by=user.id,
            created_from_chat_id=created_from_chat_id,
            chat_id=related_chat.id,
        )
        await self._storage.chats.update_meta(chat_id=related_chat.id, meta=ChatMeta(assigned_ticket_id=ticket.id))
        await self._storage.chats.update_meta(
            chat_id=created_from_chat.id,
            meta=ChatMeta(related_ticket_id=ticket.id),
        )

        await self._storage.commit_transaction()

        await self._messages.create_message(
            chat_id=related_chat.id,
            content=MessageContent(
                ticket_first_message_notification=TicketFirstMessageNotificationContent(
                    ticket_id=ticket.id,
                    created_from_chat_id=created_from_chat_id,
                ),
            ),
            initiator_id=user.id,
        )

        await self._messages.create_message(
            chat_id=created_from_chat.id,
            content=MessageContent(
                related_ticket_created_notification=RelatedTicketCreatedNotificationContent(
                    ticket_chat_id=related_chat.id,
                    ticket_id=ticket.id,
                ),
            ),
            initiator_id=user.id,
        )

        await self._messages.create_message(
            chat_id=created_from_chat.id,
            content=MessageContent(text=TextContent(text=message)),
            sender_id=user.id,
        )

        await self._updates_publisher.publish_update(
            ChatCreated(
                chat_id=related_chat.id,
                created_by_user_id=user.id,
                match_id=match_id,
                chat_type=ChatType.TICKET,
            ),
        )

        await self._updates_publisher.publish_update(
            TicketCreated(
                created_by_user_id=user.id,
                ticket_id=ticket.id,
                match_id=match_id,
                chat_id=related_chat.id,
            ),
        )

        return CreateTicketResponse(chat_id=related_chat.id, ticket_id=ticket.id)

    async def _check_able_to_create_ticket_for_match(
        self,
        user: AuthPayload,
        match_id: int | None,
        chat_id: int,
    ) -> None:
        if not match_id:
            return
        ticket = await self._storage.tickets.check_user_ticket(user_id=user.id, chat_id=chat_id, match_id=match_id)
        if ticket:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User already created ticket for this match",
            )

    async def _create_ticket_without_source_chat(
        self,
        user: AuthPayload,
        match_id: int | None,
        message: str,
    ) -> CreateTicketResponse:
        if user.role not in (Role.SCOUT, Role.BOOKMAKER):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only a scout or bookmaker can create a ticket not binded to a chat",
            )

        chat_for_ticket = await self._storage.chats.create_chat(
            match_id=match_id,
            chat_type=ChatType.TICKET,
            meta=ChatMeta(),
        )

        await self._storage.chats.add_user_to_chat(
            user_id=user.id,
            chat_id=chat_for_ticket.id,
            role=user.role,
            is_primary_member=True,
            has_read_permission=True,
            has_write_permission=True,
        )

        await self._check_able_to_create_ticket_for_match(
            user=user,
            match_id=match_id,
            chat_id=chat_for_ticket.id,
        )

        ticket = await self._storage.tickets.create_ticket(
            created_by=user.id,
            created_from_chat_id=None,
            chat_id=chat_for_ticket.id,
        )

        await self._storage.chats.update_meta(
            chat_id=chat_for_ticket.id,
            meta=ChatMeta(assigned_ticket_id=ticket.id),
        )

        await self._unread_counters.set_unread_count_by_chat_id(
            user_id=user.id,
            chat_id=chat_for_ticket.id,
            value=0,
        )

        await self._storage.commit_transaction()

        await self._messages.create_message(
            chat_id=chat_for_ticket.id,
            content=MessageContent(
                ticket_first_message_notification=TicketFirstMessageNotificationContent(
                    ticket_id=ticket.id,
                    created_from_chat_id=None,
                ),
            ),
            initiator_id=user.id,
        )

        await self._messages.create_message(
            chat_id=chat_for_ticket.id,
            content=MessageContent(text=TextContent(text=message)),
            sender_id=user.id,
        )

        await self._updates_publisher.publish_update(
            ChatCreated(
                chat_id=chat_for_ticket.id,
                created_by_user_id=user.id,
                match_id=chat_for_ticket.match_id,
                chat_type=ChatType.TICKET,
            ),
        )

        await self._updates_publisher.publish_update(
            TicketCreated(
                created_by_user_id=user.id,
                ticket_id=ticket.id,
                match_id=match_id,
                chat_id=chat_for_ticket.id,
            ),
        )

        return CreateTicketResponse(ticket_id=ticket.id, chat_id=chat_for_ticket.id)

    async def _create_chat_for_ticket_from_match(
        self,
        user: AuthPayload,
        created_from_chat: Chat,
    ) -> Chat:
        if user.role != Role.BOOKMAKER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the bookmaker can create a ticket from a chat with a scout",
            )

        if await self._storage.tickets.get_ticket_by_chat_id(created_from_chat.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A ticket already exists for this chat",
            )

        chat_members = await self._storage.chats.get_users_in_chat(
            chat_id=created_from_chat.id,
            limit=None,
            offset=None,
        )

        primary_members = [member for member in chat_members if member.is_primary_member]

        if user.id not in [member.user_id for member in primary_members]:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "User is not a primary member of the chat",
            )

        book_super_chat = await self._storage.chats.create_chat(
            match_id=created_from_chat.match_id,
            chat_type=ChatType.TICKET,
            meta=ChatMeta(),
        )

        await self._storage.chats.add_user_to_chat(
            user_id=user.id,
            chat_id=book_super_chat.id,
            role=Role.BOOKMAKER,
            is_primary_member=True,
            has_read_permission=True,
            has_write_permission=True,
        )

        await self._unread_counters.set_unread_count_by_chat_id(
            user_id=user.id,
            chat_id=book_super_chat.id,
            value=0,
        )

        return book_super_chat

    async def _validate_match_info(self, match_id: int) -> None:
        match_info = await self._storage.matches.get_match_by_id(sportlevel_id=match_id)
        if not match_info:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Match not found",
            )

        if not match_info.state.is_active:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Match is not active",
            )

    async def _notify_ticket_status_changed(
        self,
        ticket_id: int,
        old_status: TicketStatus,
        new_status: TicketStatus,
        changed_by: int,
    ) -> None:
        await self._updates_publisher.publish_update(
            TicketStatusChanged(
                changed_by_user_id=changed_by,
                ticket_id=ticket_id,
                old_status=old_status,
                new_status=new_status,
            ),
        )
