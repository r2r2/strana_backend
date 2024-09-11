from datetime import datetime
from typing import Protocol

from src.core.types import UserId
from src.entities.chats import ChatBaseInfoDTO, ChatInfo, ChatMembershipDetailsDTO, ChatMeta
from src.entities.matches import ChatType
from src.entities.users import ChatUserDTO, Role
from src.modules.storage.models.chat import Chat, ChatMembership


class ChatOperationsProtocol(Protocol):
    async def get_chat_version(self, chat_id: int) -> int | None:
        """Returns the version of the chat with the specified id"""
        ...

    async def update_chat_version(self, chat_id: int) -> None:
        """Updates the version of the chat to the new one"""
        ...

    async def get_chat_by_id(self, chat_id: int) -> Chat | None: ...

    async def get_chat_by_message_id(self, message_id: int) -> Chat | None: ...

    async def get_chat_membership_details(self, user_id: UserId, chat_id: int) -> ChatMembershipDetailsDTO | None: ...

    async def get_chat_membership_by_message_id(self, message_id: int, user_id: UserId) -> ChatMembership | None: ...

    async def is_user_in_chat(self, chat_id: int, user_id: UserId) -> bool: ...

    async def get_chats_of_user(self, user_id: UserId) -> list[int]: ...

    async def get_chat_id_between_users(self, user_1_id: UserId, user_2_id: UserId) -> int | None: ...

    async def get_all_chats_by_match(
        self,
        match_id: int,
        chat_types: list[ChatType] | None = None,
    ) -> list[ChatBaseInfoDTO]: ...

    async def get_users_in_chat(
        self,
        chat_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ChatUserDTO]: ...

    async def create_chat(
        self,
        match_id: int | None,
        chat_type: ChatType,
        meta: ChatMeta,
    ) -> Chat: ...

    async def update_meta(
        self,
        chat_id: int,
        meta: ChatMeta,
    ) -> None: ...

    async def close_chats(self, chat_ids: list[int]) -> None: ...

    async def reopen_chat(self, chat_id: int) -> None: ...

    async def add_user_to_chat(
        self,
        *,
        user_id: UserId,
        chat_id: int,
        role: Role,
        is_primary_member: bool,
        has_write_permission: bool,
        has_read_permission: bool,
    ) -> bool: ...

    async def remove_user_from_chat(self, chat_id: int, user_id: UserId) -> bool: ...

    async def get_chats(
        self,
        user_id: UserId,
        user_role: Role,
        chat_type: ChatType | None,
        match_id: int | None,
        limit: int,
        offset: int,
    ) -> list[ChatInfo]: ...

    async def get_chat(self, user_id: UserId, user_role: Role, chat_id: int) -> ChatInfo | None: ...

    async def get_role_in_chat(self, user_id: UserId, chat_id: int) -> Role | None: ...

    async def is_chat_with_scout_exists(self, match_id: int, scout_id: UserId, bookmaker_id: UserId) -> bool:
        """Checks if there is a chat between the specified scout and the bookmaker for the given match"""
        ...

    async def get_inactive_chats_to_close(self, last_message_threshold: datetime) -> list[int]: ...

    async def update_scout_membership(
        self,
        chat_id: int,
        scout_id: UserId,
        last_available_message_id: int | None = None,
        first_available_message_id: int | None = None,
        is_archive_member: bool = False,
        has_write_permission: bool = True,
    ) -> None: ...
