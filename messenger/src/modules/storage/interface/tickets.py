from typing import Protocol

from src.api.http.serializers.tickets import TicketInfo, TicketStatusFilter
from src.core.types import UserId
from src.entities.tickets import TicketCloseReason, TicketFilters, TicketStatus
from src.entities.users import Language, Role
from src.modules.storage.models.ticket import Ticket


class TicketOperationsProtocol(Protocol):
    async def create_ticket(
        self,
        created_by: UserId,
        created_from_chat_id: int | None,
        chat_id: int,
    ) -> Ticket: ...

    async def get_ticket_by_chat_id(self, chat_id: int) -> Ticket | None: ...

    async def get_ticket_by_id(self, ticket_id: int) -> Ticket | None: ...

    async def update_ticket_status(self, ticket: Ticket, new_status: TicketStatus, updated_by: UserId) -> bool: ...

    async def assign_to_user(self, ticket_id: int, user_id: int) -> None: ...

    async def close_ticket(
        self, ticket: Ticket, comment: str, reason: TicketCloseReason, updated_by: UserId
    ) -> None: ...

    async def get_ticket_detailed(
        self,
        user_id: UserId,
        user_role: Role,
        lang: Language,
        ticket_id: int,
    ) -> TicketInfo | None: ...

    async def search_tickets(
        self,
        user_id: UserId,
        user_role: Role,
        status: TicketStatusFilter | None,
        lang: Language,
        filters: TicketFilters,
        limit: int | None = ...,
        offset: int | None = ...,
    ) -> tuple[list[TicketInfo], int]: ...

    async def count_tickets(
        self,
        status: TicketStatus,
        assigned_to_user_id: int | None = None,
    ) -> int: ...

    async def check_user_ticket(self, user_id: int, match_id: int, chat_id: int) -> bool: ...
