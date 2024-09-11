from src.core.types import UserId
from src.entities.matches import ChatType
from src.entities.permissions import ChatAccessDTO
from src.entities.users import Role
from src.modules.storage.interface import StorageProtocol
from src.modules.storage.models import Message


class PermissionsController:
    async def is_chat_writable_by_user(
        self,
        chat_id: int,
        user_id: UserId,
        storage: StorageProtocol,
    ) -> tuple[bool, str | None]:
        membership = await storage.chats.get_chat_membership_details(
            chat_id=chat_id,
            user_id=user_id,
        )

        if not membership:
            return False, "The chat was not found"

        if membership.is_chat_closed:
            return False, "The chat is closed"

        if not membership.is_member:
            return False, "The user is not a member of the chat"

        if not membership.has_write_permission:
            return False, "The user does not have write permissions for this chat"

        match membership.chat_type:
            case ChatType.MATCH:
                # Second bookmaker can also chat with the scout
                # but supervisor can't write in the chat
                # and secondary scouts cannot write neither

                if membership.user_role == Role.SUPERVISOR:
                    return False, "The supervisor cannot write to the match chat"

                if membership.user_role == Role.SCOUT and not membership.is_primary_member:
                    return False, "The secondary scout cannot write to the match chat"

            case ChatType.TICKET:
                # A secondary supervisor cannot write in a ticket chat
                if membership.user_role == Role.SUPERVISOR and not membership.is_primary_member:
                    return False, "The secondary supervisor cannot write to the ticket chat"

            case ChatType.PERSONAL:
                # Regular chat, no special rules applied
                ...

            case _:
                ...

        return True, None

    async def is_chat_accessible(
        self,
        chat_id: int,
        user_id: UserId,
        user_role: Role,
        storage: StorageProtocol,
    ) -> ChatAccessDTO:
        membership = await storage.chats.get_chat_membership_details(
            chat_id=chat_id,
            user_id=user_id,
        )
        if not membership:
            return ChatAccessDTO(is_accessible=False, error_msg="The chat was not found")

        if membership.is_member:
            return ChatAccessDTO(
                is_accessible=True,
                last_available_message_id=membership.last_available_message_id,
                first_available_message_id=membership.first_available_message_id,
            )

        match membership.chat_type:
            case ChatType.PERSONAL:
                return ChatAccessDTO(is_accessible=False, error_msg="The user is not a member of the chat")

            case ChatType.MATCH:
                if user_role not in (Role.SUPERVISOR, Role.BOOKMAKER):
                    return ChatAccessDTO(is_accessible=False, error_msg="No permissions to view this chat")

            case ChatType.TICKET:
                if user_role != Role.SUPERVISOR:
                    return ChatAccessDTO(is_accessible=False, error_msg="Only supervisors have access to this chat")

            case _:
                ...

        return ChatAccessDTO(
            is_accessible=True,
            last_available_message_id=membership.last_available_message_id,
            first_available_message_id=membership.first_available_message_id,
        )

    async def check_message_edit_permissions(
        self,
        user_id: UserId,
        message_id: int,
        storage: StorageProtocol,
    ) -> tuple[bool, Message | None]:
        message = await storage.messages.get_message_by_id(message_id)
        if not message or message.sender_id != user_id:
            return False, message
        return True, message
